# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Đoàn Quang Thanh
- **MSSV:** 2A202602841
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/dqtxdy/K4-L3-DAY13-DoanQuangThanh-2A202602841-Monitoring-LLMOps
- **Commit SHA cuối:** `332c486bb0241fa1f58d7697e47b9cd80637fe6c`.
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602841`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | [`evidence/01-pytest.txt`](evidence/01-pytest.txt) |
| Log validator | [`evidence/02-log-validator.txt`](evidence/02-log-validator.txt) |
| Dashboard validator | [`evidence/03-dashboard-validator.txt`](evidence/03-dashboard-validator.txt) |
| Structured log | [`evidence/04-structured-log.png`](evidence/04-structured-log.png), [`evidence/04-structured-log.jsonl`](evidence/04-structured-log.jsonl) |
| PII redaction | [`evidence/05-pii-redaction.png`](evidence/05-pii-redaction.png), [`evidence/05-pii-redaction.txt`](evidence/05-pii-redaction.txt) |
| Trace list | [`evidence/06-trace-list.png`](evidence/06-trace-list.png) |
| Trace waterfall | [`evidence/07-trace-waterfall.png`](evidence/07-trace-waterfall.png) |
| Trace metadata | [`evidence/08-trace-metadata.png`](evidence/08-trace-metadata.png) |
| Prompt versions | [`evidence/09-prompt-versions.png`](evidence/09-prompt-versions.png) |
| Prompt rollback | [`evidence/10-prompt-rollback-before.png`](evidence/10-prompt-rollback-before.png), [`evidence/10-prompt-rollback-after.png`](evidence/10-prompt-rollback-after.png) |
| Dashboard runtime | [`evidence/11-dashboard-overview.png`](evidence/11-dashboard-overview.png) |
| Incident metric | [`evidence/12-incident-metric.png`](evidence/12-incident-metric.png), [`evidence/12-incident-metric.txt`](evidence/12-incident-metric.txt) |
| Incident log | [`evidence/13-incident-log.png`](evidence/13-incident-log.png), [`evidence/13-incident-log.jsonl`](evidence/13-incident-log.jsonl) |
| Incident trace | [`evidence/14-incident-trace.png`](evidence/14-incident-trace.png), [`evidence/14-incident-trace.txt`](evidence/14-incident-trace.txt) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Exit 1: `data/logs.jsonl` chưa tồn tại | 100/100; 20 records, 10 correlation IDs | `evidence/02-log-validator.txt` |
| `validate_dashboard.py` | 6/6 | 6/6 | `evidence/03-dashboard-validator.txt` |
| `pytest` | Collection error: dependencies missing | 26 passed in 1.92s | `evidence/01-pytest.txt` |
| Số traces hợp lệ | Chưa có | 24 root trace có đủ retrieval/generation; 14 trace dùng managed prompt | Langfuse Observations API v2 |
| Số PII leak | Chưa có runtime log | 0 trong 20 records của corpus cuối | `evidence/02-log-validator.txt`, `evidence/05-pii-redaction.txt` |
| Latency P95 / TTFT P95 | Chưa có | 150 ms / 50 ms trong cửa sổ 60 phút | `evidence/11-dashboard-overview.png` |
| Retrieval success rate | Chưa có | 100% trong workload 10 request hiển thị trên dashboard | `evidence/11-dashboard-overview.png` |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** middleware nhận `x-request-id` hợp lệ hoặc sinh `req-<8 hex>`, bind qua structlog contextvars, trả lại `x-request-id` và `x-response-time-ms`; context được reset ở đầu/cuối request.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, event, correlation ID, latency/TTFT, token, cost, quality và retrieval status theo event.
- **Cách bảo đảm PII được scrub trước khi ghi:** processor đệ quy chạy trước `JsonlFileProcessor` và JSON renderer, bao gồm string lồng trong payload và exception.
- **Cách kiểm chứng kết quả:** 26 test pass; log validator không phát hiện PII trong 20 records của corpus cuối. Canary email, điện thoại, CCCD và thẻ đã được redact trước khi ghi; trace metadata được kiểm tra không có PII thô.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Observations API v2 ghi nhận 24 root trace trong project `day13-k4-l3b-2A202602841`; 14 trace dùng managed prompt.
- **Cấu trúc root/retrieval/generation observations:** 24/24 root `lab-agent-run` có child `retrieval` và `generation`. Generation ghi model, usage, cost estimate và prompt linkage.
- **Cách nối trace với log:** correlation ID trong structured log khớp metadata trace; ví dụ `req-3831fed9` trong trace `64fd75aabb757f9c63c837baec12c2eb`.
- **Prompt name:** `day13-chat`.
- **Version/label baseline:** v1 với label `baseline` và `production`.
- **Version/label candidate:** v2 với label `candidate`; `production` đã chuyển sang v2 rồi rollback về v1.
- **Trace ID của mỗi version:** baseline v1 `4af9e41823d79b7e39a6ac2bd0fab7fc`; candidate v2 `eb3357d5c646d0292bb84bfe0839ed07`; production v2 `64fd75aabb757f9c63c837baec12c2eb`; rollback v1 `43219092e7930b9e28a3f1f1418d44db`.
- **Cách promote và rollback `production`:** resolve prompt theo label, cập nhật label production và chạy lại cùng input; version trong trace là version Langfuse resolve thực tế, theo chuỗi 1 → 2 → 1.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** latency/TTFT, traffic, errors/retrieval, cost, tokens và quality được tính từ `data/logs.jsonl`; threshold hiển thị lần lượt gồm P95 ≤3000 ms, ≥1 request/min, error ≤2%, retrieval ≥90%, cost ≤$2.5, tokens ≤50,000 và quality ≥0.75.
- **SLO và lý do chọn:** SLI là request thành công với latency ≤3000 ms; target 99.5% trong cửa sổ 28 ngày theo `config/slo.yaml`. Ba giây là ngưỡng lab của panel latency.
- **Cách tính error budget:** 100% − 99.5% = 0.5% trong 28 ngày; tương đương tối đa 50 request không đạt trên 10,000 request.
- **Ba alert và runbook tương ứng:** P95 >3000 ms/5m, error rate >2%/5m, retrieval success <90%/5m; owner `student-2A202602841`, channel `slack`, runbook tại `docs/alerts.md`.

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:** 2026-09-30T05:13:51.180652+00:00 đến 2026-09-30T05:14:04.957257+00:00.
- **Triệu chứng từ metrics:** 5/5 response vượt ngưỡng challenge 2000 ms; P50 2652 ms, P95/P99 3067 ms; TTFT P95 50 ms, error rate 0%.
- **Log line và correlation ID liên quan:** event `response_sent`, `correlation_id=req-68327b43`, `latency_ms=3067`, `tool_success=true` trong `evidence/13-incident-log.jsonl`.
- **Trace ID và span gây ảnh hưởng:** trace `9df0c93f6219d8ee11b7247068523f44`; retrieval span `86c806cd0cb4c5f2` mất 2.501 s, generation span `039f37f9feffb8e7` mất 0.150 s. Cùng correlation ID `req-68327b43`.
- **Root cause:** incident `rag_slow` làm retrieval chờ 2.5 s; lời gọi đồng bộ `run()` chặn event loop ở route async, tuần tự hóa 5 request concurrent.
- **Fix action:** tắt incident bằng `python scripts/inject_incident.py --disable` và dispatch hàm đồng bộ `run()` qua `run_in_threadpool()`.
- **Preventive measure:** giữ blocking SDK calls trong threadpool hoặc dùng async client; theo dõi retrieval latency và duy trì concurrency test.

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** PII scrub chạy trước file writer để payload lồng nhau và exception không bị serialize trước khi redact.
- **Một lỗi/blocker đã gặp:** endpoint legacy `/api/public/traces` không trả observations trên workspace; dùng Langfuse Observations API v2 để đọc traces.
- **Cách tìm nguyên nhân và xử lý:** đối chiếu metric, log cùng correlation ID và trace waterfall; retrieval span chiếm phần lớn root duration, sau đó tắt incident và chuyển tác vụ đồng bộ sang threadpool.
- **Cách hiểu luồng Metrics → Logs → Traces:** metric khoanh triệu chứng/time window; log xác định request qua correlation ID; trace cùng ID chỉ ra span bất thường; root cause được kết luận khi ba nguồn khớp.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** label resolve tới version cụ thể; token/cost giúp theo dõi thay đổi workload; SLO quy định tỷ lệ thành công và error budget; rollback đưa production về version đã biết.
- **Điều quan trọng nhất đã học:** validator cấu trúc không thay thế runtime evidence.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** recovery workload dùng RAG/LLM stub, không đo latency dịch vụ ngoài. Ảnh 04/05/11 ghi lại structured log, PII redaction và dashboard runtime; dashboard hiển thị 6 panel cùng time range và threshold.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
