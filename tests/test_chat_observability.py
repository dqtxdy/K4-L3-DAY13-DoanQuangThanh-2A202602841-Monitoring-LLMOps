from __future__ import annotations

import json
import asyncio
import re
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import httpx

from app import logging_config
from app import main as main_module
from app.main import app


def test_chat_response_log_exposes_quality_for_dashboard(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    async def send_request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            return await client.post(
                "/chat",
                json={
                    "user_id": "student-01",
                    "session_id": "session-01",
                    "feature": "qa",
                    "message": "Explain observability",
                },
            )

    response = asyncio.run(send_request())

    assert response.status_code == 200
    assert response.headers["x-request-id"] == response.json()["correlation_id"]
    assert re.fullmatch(r"req-[0-9a-f]{8}", response.headers["x-request-id"])
    assert "x-response-time-ms" in response.headers
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    response_event = next(event for event in events if event["event"] == "response_sent")
    assert response_event["quality_score"] == response.json()["quality_score"]
    assert response_event["ttft_ms"] == response.json()["ttft_ms"]
    assert response_event["tool_name"] == "retrieval"
    assert response_event["tool_success"] is True


def test_request_id_is_echoed_or_regenerated_without_context_leak(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)
    payload = {
        "user_id": "student-02",
        "session_id": "session-02",
        "feature": "qa",
        "message": "Explain request correlation",
    }

    async def send_requests() -> tuple[httpx.Response, httpx.Response]:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            supplied = await client.post(
                "/chat", json=payload, headers={"x-request-id": "client-trace-42"}
            )
            invalid = await client.post(
                "/chat", json=payload, headers={"x-request-id": "bad id"}
            )
            return supplied, invalid

    supplied, regenerated = asyncio.run(send_requests())
    assert supplied.headers["x-request-id"] == "client-trace-42"
    assert supplied.json()["correlation_id"] == "client-trace-42"
    assert re.fullmatch(r"req-[0-9a-f]{8}", regenerated.headers["x-request-id"])
    assert regenerated.json()["correlation_id"] == regenerated.headers["x-request-id"]
    assert regenerated.headers["x-request-id"] != "client-trace-42"

    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    request_ids = [event["correlation_id"] for event in events if event["event"] == "request_received"]
    assert request_ids == ["client-trace-42", regenerated.headers["x-request-id"]]


def test_blocking_agent_runs_off_event_loop_under_concurrency(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)
    active = 0
    max_active = 0
    lock = threading.Lock()

    def slow_agent(**kwargs):
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
        time.sleep(0.08)
        with lock:
            active -= 1
        return SimpleNamespace(
            answer="Test response",
            latency_ms=80,
            ttft_ms=10,
            tokens_in=20,
            tokens_out=10,
            cost_usd=0.001,
            quality_score=0.9,
        )

    monkeypatch.setattr(main_module.agent, "run", slow_agent)
    payload = {
        "user_id": "student-concurrency",
        "session_id": "session-concurrency",
        "feature": "qa",
        "message": "Check concurrent request handling",
    }

    async def send_requests() -> list[httpx.Response]:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await asyncio.gather(
                *(client.post("/chat", json=payload) for _ in range(5))
            )

    responses = asyncio.run(send_requests())
    assert all(response.status_code == 200 for response in responses)
    assert len({response.headers["x-request-id"] for response in responses}) == 5
    assert max_active >= 2
