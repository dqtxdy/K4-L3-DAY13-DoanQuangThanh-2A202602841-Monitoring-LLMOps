# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Runtime verification có thật được lưu trong `evidence/`. Official challenge đã chạy và được điều tra; ảnh incident 12–14 đã lưu.

## 1. Thông tin học viên

- **Họ và tên:** Đoàn Quang Thanh
- **MSSV:** 2A202602841
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/dqtxdy/K4-L3-DAY13-DoanQuangThanh-2A202602841-Monitoring-LLMOpsK4-L3B-Day13-Monitoring-LLMOps
- **Commit SHA cuối:** lấy giá trị sau khi push bằng `git rev-parse HEAD` và nộp cùng URL repository trên LMS/Codelabs.
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1` (cohort K4; file gốc được giữ local và ignored).
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602841` (verified qua API sau khi đổi tên).

## 2. Evidence index

Các file text/JSON dưới đây là output runtime/API thật. Screenshot là ảnh UI thật; ảnh 06 đã che khu vực tài khoản, ảnh 08 đã che giá trị public key, các ảnh 07/09/10 là bản chụp mới có project context cần thiết.

| Evidence | Đường dẫn / trạng thái |
|---|---|
| Pytest cuối | [`evidence/01-pytest.txt`](evidence/01-pytest.txt) |
| Log validator | [`evidence/02-log-validator.txt`](evidence/02-log-validator.txt) |
| Dashboard validator | [`evidence/03-dashboard-validator.txt`](evidence/03-dashboard-validator.txt) |
| Structured log | [`evidence/04-structured-log.jsonl`](evidence/04-structured-log.jsonl), `04-structured-log.png` (runtime screenshot; chữ nhỏ, cần chụp rõ hơn nếu có thể) |
| PII redaction | [`evidence/05-pii-redaction.txt`](evidence/05-pii-redaction.txt), `05-pii-redaction.png` |
| Trace list | [`evidence/06-trace-list.txt`](evidence/06-trace-list.txt); `06-trace-list.png` (ảnh thật; che khu vực tài khoản ở góc trái dưới) |
| Trace waterfall | [`evidence/07-trace-waterfall.txt`](evidence/07-trace-waterfall.txt), `07-trace-waterfall.png` (ảnh chụp mới, có project title và trace tree) |
| Trace metadata | [`evidence/08-trace-metadata.txt`](evidence/08-trace-metadata.txt); `08-trace-metadata.png` (ảnh thật; đã che giá trị `scope.attributes.public_key`) |
| Prompt versions | [`evidence/09-prompt-versions.txt`](evidence/09-prompt-versions.txt), `09-prompt-versions.png` (ảnh chụp mới, hiển thị v1/v2 và project title) |
| Prompt rollback | [`evidence/10-prompt-rollback.txt`](evidence/10-prompt-rollback.txt); `10-prompt-rollback-before.png` (v2 production), `10-prompt-rollback-after.png` (rollback về v1) |
| Dashboard runtime | [`evidence/11-dashboard-runtime.txt`](evidence/11-dashboard-runtime.txt), `11-dashboard-overview.png` |
| Incident metric | [`evidence/12-incident-metric.txt`](evidence/12-incident-metric.txt); [`evidence/12-incident-metric.png`](evidence/12-incident-metric.png) |
| Incident log | [`evidence/13-incident-log.jsonl`](evidence/13-incident-log.jsonl); [`evidence/13-incident-log.png`](evidence/13-incident-log.png) (mở ảnh ở độ phân giải gốc để đọc JSON) |
| Incident trace | [`evidence/14-incident-trace.txt`](evidence/14-incident-trace.txt); [`evidence/14-incident-trace.png`](evidence/14-incident-trace.png) (giá trị public key đã che) |
| Recovery | [`evidence/15-incident-recovery.txt`](evidence/15-incident-recovery.txt) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline thực tế | Kết quả cuối hiện có | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Exit 1: `data/logs.jsonl` not found | 100/100; 64 records, 32 unique correlation IDs | `evidence/02-log-validator.txt` |
| `validate_dashboard.py` | 6/6 | 6/6 | `evidence/03-dashboard-validator.txt` |
| `pytest` | Collection error: dependencies missing | 26 passed after the incident concurrency fix | [`evidence/01-pytest.txt`](evidence/01-pytest.txt) |
| Số traces | Chưa có | 24 root traces; 24 đủ root/retrieval/generation; 14 managed-prompt traces | Langfuse Observations API v2; evidence 06–08 |
| Số PII leak | Chưa có runtime log | 0/64 runtime records in final validation | `evidence/05-pii-redaction.txt` |
| Latency P95 / TTFT P95 | Chưa có | 489 ms / 50 ms trong cửa sổ 60 phút | `evidence/11-dashboard-runtime.txt` |
| Retrieval success rate | Chưa có | 100% (44/44 response thành công) | Runtime logs |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** middleware nhận `x-request-id` nếu chỉ chứa ký tự an toàn và dài tối đa 128; nếu thiếu/không hợp lệ, sinh `req-<8 hex>`. ID được bind bằng structlog contextvars, trả qua `x-request-id`; `x-response-time-ms` trả thời gian middleware. Context được clear ở đầu/cuối request.
- **Các metadata được ghi vào structured log:** `user_id_hash` (SHA-256 rút gọn), `session_id`, `feature`, `model`, `env`, cùng event, correlation ID, latency/TTFT, token, cost, quality và retrieval status theo event.
- **Cách bảo đảm PII được scrub trước khi ghi:** processor đệ quy chạy sau format exception, trước `JsonlFileProcessor` và JSON renderer. Redaction áp dụng trên mọi string trong dict/list/tuple, gồm payload và lỗi.
- **Cách kiểm chứng kết quả:** Full suite 26 passed after the incident fix (`evidence/01-pytest.txt`). Final validator không phát hiện PII trong 64 runtime records; canary email/card được redacted trong log. Runtime samples nằm ở evidence 04/05.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Observations API v2 trả về 24 root traces và 72 observations trong project `day13-k4-l3b-2A202602841`; 14 traces dùng managed prompt.
- **Cấu trúc root/retrieval/generation observations:** đã xác minh 24/24 cây có root `lab-agent-run` và children `retrieval`, `generation`. Generation có model, token usage, estimated cost, TTFT, latency và prompt linkage. Mock estimate dùng $3/1M input tokens và $15/1M output tokens; đây không phải hóa đơn model thật.
- **Cách nối trace với log:** correlation ID khớp giữa root/child trace metadata và JSONL runtime; ví dụ v2 production `req-3831fed9` trong trace `64fd75aabb757f9c63c837baec12c2eb`.
- **Prompt name:** `day13-chat` (cấu hình qua `LANGFUSE_PROMPT_NAME`).
- **Version/label baseline:** v1 labels `baseline`, `production`.
- **Version/label candidate:** v2 label `candidate`; đã promote `production` sang v2, sau đó rollback về v1.
- **Trace ID của mỗi version:** baseline v1 `4af9e41823d79b7e39a6ac2bd0fab7fc` / `req-56cea1f8`; candidate v2 `eb3357d5c646d0292bb84bfe0839ed07` / `req-3af9eabe`; production v2 `64fd75aabb757f9c63c837baec12c2eb` / `req-3831fed9`; rollback production v1 `43219092e7930b9e28a3f1f1418d44db` / `req-84b86246`.
- **Cách promote và rollback `production`:** gọi Langfuse update theo version rồi resolve label thực tế; live sequence trả 1 → 2 → 1. App ghi version Langfuse trả về, không gán cứng.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** `config/dashboard.yaml` quy định latency P50/P95/P99 + TTFT, traffic, errors/retrieval, cost, tokens và quality. Renderer đọc 89 JSONL records thật trong lần baseline đã ghi evidence 11 và tạo `data/dashboard.html`; baseline P95 489 ms, TTFT P95 50 ms. Challenge snapshot (evidence 12) đo P95 3067 ms, vượt threshold challenge 2000 ms.
- **SLO và lý do chọn:** [`config/slo.yaml`](../config/slo.yaml) đặt SLI là request thành công với latency ≤3000 ms trong cửa sổ 28 ngày, target 99.5%. Ngưỡng 3 giây là threshold lab tương ứng panel latency, không phải kết quả baseline đo được.
- **Cách tính error budget:** 100% − 99.5% = 0.5% trong 28 ngày; ví dụ 10,000 requests có tối đa 50 request không đạt. SLI dùng event response hợp lệ trong tổng số request nhận.
- **Ba alert và runbook tương ứng:** [`config/alert_rules.yaml`](../config/alert_rules.yaml) định nghĩa P95 >3000 ms/5m, error rate >2%/5m, retrieval success <90%/5m. Cả ba có severity, owner `student-repository-owner`, Slack `#k4-l3b-alerts`, và runbook tại [`docs/alerts.md`](../docs/alerts.md). Alert runtime chưa được triển khai tới dịch vụ Slack.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`; cohort K4. `config/challenge.json` là file Lab Coach cấp, bị ignore và không nằm trong commit.
- **Khoảng thời gian điều tra:** 2026-09-30 05:13:51–05:14:04 UTC (12:13:51–12:14:04 Asia/Ho_Chi_Minh).
- **Triệu chứng từ metrics:** ngưỡng chính thức là 2000 ms. Năm response đều HTTP 200 nhưng 5/5 vượt ngưỡng; latency app P50 2652 ms, P95/P99 3067 ms. TTFT P95 50 ms; error rate 0%. Client load test với concurrency 5 báo xấp xỉ 13.8 s/request.
- **Log line và correlation ID liên quan:** `evidence/13-incident-log.jsonl`, event `response_sent`, `correlation_id=req-68327b43`, `latency_ms=3067`, `tool_success=true`.
- **Trace ID và span gây ảnh hưởng:** trace `9df0c93f6219d8ee11b7247068523f44`, cùng correlation ID `req-68327b43`. Retrieval child span `86c806cd0cb4c5f2` mất 2.501 s; generation child `039f37f9feffb8e7` mất 0.150 s. Root duration 3.068 s. Chi tiết đã lọc input/output và resource attributes trong `evidence/14-incident-trace.txt`.
- **Root cause:** challenge inject `rag_slow` làm retrieval path chờ 2.5 s, cao hơn ngưỡng 2 s. Đồng thời `agent.run()` là hàm đồng bộ được gọi trực tiếp trong async route; blocking wait chặn event loop và xếp hàng năm request concurrent. Trace xác nhận retrieval chiếm phần lớn root duration, generation không phải bottleneck.
- **Fix action:** disable incident bằng `python scripts/inject_incident.py --disable`; sau đó chuyển lời gọi đồng bộ sang Starlette `run_in_threadpool`. Health xác nhận incident false. Normal concurrent workload sau fix trả 10/10 HTTP 200, client latency 156.6–165.2 ms; app P95 153 ms (`evidence/15-incident-recovery.txt`).
- **Preventive measure:** giữ blocking RAG/LLM SDK calls trong threadpool hoặc chuyển sang async clients; theo dõi retrieval latency riêng và đặt cảnh báo trước ngưỡng SLO. Bài test concurrency mới xác nhận nhiều lời gọi agent có thể chạy đồng thời.

Investigation evidence giữ riêng metric → log → trace cho cùng request; không lưu query/prompt preview hoặc file challenge vào evidence.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** PII scrub áp dụng đệ quy ngay trong pipeline trước file writer, để nested payload/exception strings không bị serialize trước khi che.
- **Một lỗi/blocker đã gặp:** ban đầu sandbox thiếu DNS ra PyPI/Langfuse và chặn localhost sockets; workload chạy bằng ASGI transport sau đó gửi được tới Langfuse khi được cấp quyền mạng.
- **Cách tìm nguyên nhân và xử lý:** dùng test suite/validators, kiểm tra API responses và Langfuse Observations API v2. Langfuse account mới không hỗ trợ legacy `/api/public/traces`; chuyển sang endpoint Observations v2 để đọc observations.
- **Cách hiểu luồng Metrics → Logs → Traces:** metric khoanh triệu chứng và time window; log chọn request bằng correlation ID; trace cùng correlation ID cho thấy span retrieval/generation bất thường; root cause chỉ kết luận khi cả ba nguồn khớp.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** prompt label trỏ tới version được resolve thực tế; token/cost giúp phát hiện prompt phình; SLO xác định tỷ lệ request tốt còn error budget biểu thị mức lỗi cho phép; rollback label đưa production về version đã biết.
- **Điều quan trọng nhất đã học:** validator cấu trúc không chứng minh runtime behavior hoặc evidence.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** in-app browser không khả dụng để Agent tự chụp; người dùng đã cung cấp screenshot thật cho dashboard/Langfuse. Ảnh 04 còn nhỏ chữ, có thể chụp rõ hơn. Official challenge đã điều tra; còn thiếu screenshot PNG 12–14. Runtime recovery dùng fake RAG/LLM, không chứng minh latency của dịch vụ ngoài. Langfuse exporter trả HTTP 401 khi shutdown recovery run, nên không tính trace recovery là evidence.

## 9. Checklist trước khi nộp

- [x] Thông tin học viên và repository URL đã được điền; commit SHA phải cập nhật sau commit.
- [x] Tests/validators đã chạy; sau fix 26 tests pass, log validator 100/100, dashboard validator 6/6.
- [x] Workload runtime tạo log sạch PII và dashboard HTML có dữ liệu.
- [x] Tạo v1/v2, chạy ≥10 managed prompt requests, xác minh trace tree, prompt versions, promote/rollback.
- [x] Đổi tên project Langfuse theo format cá nhân.
- [x] Lưu screenshot dashboard và Langfuse theo `docs/SUBMISSION.md` (ảnh 04 nên chụp rõ hơn nếu có thể).
- [x] Điều tra official challenge theo metric → log → trace; challenge gốc vẫn ignored và không được commit.
- [x] Lưu screenshot incident metric (12) và trace (14); giá trị public key trong ảnh 14 đã được che.
- [x] Lưu incident log (13); mở ảnh ở độ phân giải gốc để đọc JSON.
- [x] Kiểm tra không có secret, PII thô hoặc artifact không cần thiết.
