"""Render a six-panel HTML dashboard from the application's JSONL runtime logs."""
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_records(path: Path, minutes: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            stamp = datetime.fromisoformat(item["ts"].replace("Z", "+00:00"))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid JSONL record at line {line_number}: {exc}") from exc
        if stamp >= cutoff:
            records.append(item)
    return records


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, round((p / 100) * (len(ordered) - 1))))]


def display(value, unit="") -> str:
    return "No data" if value is None else f"{value:g}{unit}"


def build_html(records: list[dict], minutes: int) -> str:
    received = [r for r in records if r.get("event") == "request_received"]
    sent = [r for r in records if r.get("event") == "response_sent"]
    failed = [r for r in records if r.get("event") == "request_failed"]
    tool_rows = [r for r in sent + failed if r.get("tool_success") is not None]
    latencies = [float(r["latency_ms"]) for r in sent if isinstance(r.get("latency_ms"), (int, float))]
    ttft = [float(r["ttft_ms"]) for r in sent if isinstance(r.get("ttft_ms"), (int, float))]
    costs = [float(r["cost_usd"]) for r in sent if isinstance(r.get("cost_usd"), (int, float))]
    token_in = sum(r.get("tokens_in", 0) for r in sent if isinstance(r.get("tokens_in"), (int, float)))
    token_out = sum(r.get("tokens_out", 0) for r in sent if isinstance(r.get("tokens_out"), (int, float)))
    scores = [float(r["quality_score"]) for r in sent if isinstance(r.get("quality_score"), (int, float))]
    error_rate = len(failed) / len(received) * 100 if received else None
    retrieval_rate = sum(r.get("tool_success") is True for r in tool_rows) / len(tool_rows) * 100 if tool_rows else None
    per_minute = len(received) / minutes

    panels = [
        ("Latency · ms", f"P50 {display(percentile(latencies, 50), ' ms')} · P95 {display(percentile(latencies, 95), ' ms')} · P99 {display(percentile(latencies, 99), ' ms')} · TTFT P95 {display(percentile(ttft, 95), ' ms')}", "SLO threshold: P95 ≤ 3000 ms"),
        ("Traffic · requests/min", f"{per_minute:.2f} requests/min · {len(received)} requests", "Threshold: ≥ 1 request/min"),
        ("Errors / retrieval · percent", f"Error rate {display(error_rate, '%')} · Retrieval success {display(retrieval_rate, '%')}", "Thresholds: errors ≤ 2% · retrieval success ≥ 90%"),
        ("Cost · USD", f"${sum(costs):.6f} total · ${sum(costs) / minutes:.6f}/min", "Threshold: ≤ $2.5 total"),
        ("Tokens · tokens", f"Input {token_in:,} · Output {token_out:,}", "Threshold: ≤ 50,000 tokens"),
        ("Quality proxy · score 0–1", f"Mean {display(sum(scores) / len(scores) if scores else None)}", "Threshold: mean ≥ 0.75"),
    ]
    cards = "\n".join(
        f'<section class="panel"><h2>{html.escape(title)}</h2><p class="value">{html.escape(value)}</p><p class="threshold">{html.escape(threshold)}</p></section>'
        for title, value, threshold in panels
    )
    updated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="30"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Day 13 Monitoring Dashboard</title><style>
body{{font:16px system-ui,sans-serif;background:#101827;color:#e5edf8;margin:0;padding:2rem}}header{{max-width:1200px;margin:0 auto 1.5rem}}.grid{{max-width:1200px;margin:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1rem}}.panel{{background:#1b293c;border:1px solid #34465f;border-radius:12px;padding:1.1rem;min-height:145px}}h1{{margin:0}}h2{{font-size:1rem;color:#b9d8ff;margin-top:0}}.value{{font-size:1.35rem;font-weight:650}}.threshold,small{{color:#a8b8ca}}.empty{{color:#ffcf76}}</style></head><body><header><h1>K4-L3B Day 13 · Runtime dashboard</h1><p>Source: data/logs.jsonl · Time range: last {minutes} minutes · Refresh: 30 seconds · Updated {updated}</p>{'<p class="empty">No records in this time range yet. Start the API and send the sample workload.</p>' if not records else ''}</header><main class="grid">{cards}</main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--logs", type=Path, default=ROOT / "data/logs.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "data/dashboard.html")
    parser.add_argument("--minutes", type=int, default=60)
    args = parser.parse_args()
    if args.minutes <= 0:
        parser.error("--minutes must be positive")
    if not args.logs.exists():
        parser.error(f"runtime log file not found: {args.logs}; start the API and run load_test.py")
    try:
        records = load_records(args.logs, args.minutes)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(records, args.minutes), encoding="utf-8")
    print(f"Rendered 6 runtime panels from {len(records)} records: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
