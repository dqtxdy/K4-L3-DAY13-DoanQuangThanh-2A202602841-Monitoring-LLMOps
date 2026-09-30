# Alerts and runbooks

All three rules in `config/alert_rules.yaml` are symptoms calculated from the application JSONL events. The Slack destination is `#k4-l3b-alerts`; the owner is the student on-call for this individual lab. Use a five-minute evaluation window and the dashboard's last-60-minute view.

## Alert 1 — HighLatencyP95

- Severity: warning. Trigger: `response_sent.latency_ms` P95 exceeds 3000 ms continuously for 5 minutes.
- User impact: replies arrive slowly. Owner: student on-call. Slack: `#k4-l3b-alerts`.
- Runbook:
  1. Open the latency panel, set the window to the alert interval, and compare P50/P95/P99 with the 3000 ms SLO threshold and TTFT P95.
  2. Filter `data/logs.jsonl` `response_sent` records in that interval, order by `latency_ms`, and select an affected request's `correlation_id`.
  3. Open the Langfuse trace with that correlation ID. Compare `retrieval` and `generation` duration/status to locate the slow span.
  4. Mitigate from evidence: disable the active practice scenario, restore known-good prompt label/configuration, or reduce load. Preserve the relevant interval and IDs in the incident note.
  5. Verify P95 remains under 3000 ms for at least 5 minutes, errors are stable, and new traces use the expected prompt version. Escalate if it persists after mitigation.

## Alert 2 — HighRequestErrorRate

- Severity: critical. Trigger: failed requests divided by received requests exceeds 2% continuously for 5 minutes.
- User impact: requests fail instead of returning an answer. Owner: student on-call. Slack: `#k4-l3b-alerts`.
- Runbook:
  1. Open the errors panel for the alert interval; confirm the denominator and error types, and check retrieval success alongside HTTP failures.
  2. Filter `request_failed` records in `data/logs.jsonl` for the same interval. Record `error_type` and `correlation_id`; do not copy message content containing user data.
  3. Find the matching Langfuse trace and inspect the errored retrieval/generation observation and status message.
  4. Mitigate by disabling a failing practice fault or reverting the implicated prompt/config only when the trace supports that action. Escalate repeated dependency failures.
  5. Verify new requests produce `response_sent`, error rate falls below 2% for 5 minutes, and a fresh matching trace completes successfully.

## Alert 3 — LowRetrievalSuccess

- Severity: warning. Trigger: retrieval `tool_success` rate falls below 90% continuously for 5 minutes.
- User impact: answers may lack supporting context or requests may fail. Owner: student on-call. Slack: `#k4-l3b-alerts`.
- Runbook:
  1. Open the errors/retrieval panel for the interval and distinguish failed retrieval calls from successful calls returning no context.
  2. Filter `response_sent` and `request_failed` JSONL records with `tool_name=retrieval` and `tool_success=false`; record a relevant `correlation_id`.
  3. Open its Langfuse trace and inspect retrieval status, latency, and `context_found` metadata before generation.
  4. Disable the practice fault if active. For real failures, restore the last known-good retrieval configuration and escalate dependency outages; do not mask retrieval failure as success.
  5. Verify retrieval success returns above 90% for 5 minutes and fresh traces show expected context-found behavior.
