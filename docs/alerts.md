# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms` trong SLO 99.5% / 28 ngày
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency, xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh retrieval và generation để xác định span bất thường.
- Mitigation tạm thời: dựa trên trace để tắt incident đang bật, rollback prompt hoặc giảm tải; xác nhận P95 trở lại dưới 3000 ms.
- Owner: `student-2A202602841`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ request thành công theo SLO 99.5% / 28 ngày
- Điều kiện và thời gian duy trì: `request_failed / request_received > 2%` trong 5 phút
- Ảnh hưởng tới người dùng: request thất bại thay vì trả câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard errors, xác nhận error rate và khoảng thời gian tăng.
  2. Lọc `request_failed` trong `data/logs.jsonl`, ghi `error_type` và `correlation_id` đại diện.
  3. Mở trace cùng `correlation_id` trên Langfuse, kiểm tra status của retrieval và generation.
- Mitigation tạm thời: dựa trên error type và trace để tắt incident đang bật hoặc khôi phục cấu hình gần nhất đã biết là tốt; kiểm tra error rate giảm dưới 2%.
- Owner: `student-2A202602841`

## Alert 3

- Tên: `LowRetrievalSuccess`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ retrieval `tool_success` thành công, ngưỡng vận hành 90%
- Điều kiện và thời gian duy trì: `retrieval tool_success rate < 90%` trong 5 phút
- Ảnh hưởng tới người dùng: câu trả lời có thể thiếu context hoặc request có thể thất bại
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard errors/retrieval, xác định khoảng thời gian và tỷ lệ retrieval thành công.
  2. Lọc log trong `data/logs.jsonl` theo `tool_name=retrieval`, lấy `correlation_id` có `tool_success=false`.
  3. Mở trace cùng `correlation_id` trên Langfuse, kiểm tra retrieval status và `context_found`.
- Mitigation tạm thời: tắt practice incident nếu đang bật; nếu là lỗi thật, khôi phục retrieval config gần nhất đã biết là tốt và xác minh retrieval success vượt 90%.
- Owner: `student-2A202602841`
