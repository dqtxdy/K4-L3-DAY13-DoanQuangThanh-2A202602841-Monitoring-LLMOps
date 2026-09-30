from __future__ import annotations

import json
import asyncio
import re
from pathlib import Path

import httpx

from app import logging_config
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
