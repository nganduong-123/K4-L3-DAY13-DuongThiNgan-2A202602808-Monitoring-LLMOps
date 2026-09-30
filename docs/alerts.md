# Alert và runbook vận hành

Các alert dưới đây dựa trên triệu chứng mà người dùng quan sát được. Kênh nhận cảnh báo là Slack `#k4-l3b-alerts`; owner là `student-2A202602808`.

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`; duration: `5m`.
- SLI/SLO: P95 của `response_sent.latency_ms`; cảnh báo khi lớn hơn `3000 ms` liên tục 5 phút.
- Ảnh hưởng: người dùng chờ lâu hơn trước khi nhận câu trả lời.
- Kiểm tra: (1) xác nhận P95/P99 và khoảng thời gian trên dashboard; (2) lọc `response_sent` chậm trong `data/logs.jsonl` và lấy `correlation_id`; (3) mở trace cùng ID, so sánh thời gian retrieval và generation.
- Mitigation: giảm concurrency nếu quá tải; nếu retrieval chậm thì khôi phục nguồn dữ liệu/cấu hình; nếu generation tăng token thì rollback prompt production.

## Alert 2

- Tên: `HighRequestErrorRate`
- Severity: `critical`; duration: `5m`.
- SLI/SLO: tỷ lệ `request_failed / request_received`; cảnh báo khi lớn hơn `2%` liên tục 5 phút.
- Ảnh hưởng: người dùng nhận HTTP 500 hoặc không có câu trả lời.
- Kiểm tra: (1) xem error rate và breakdown; (2) lọc `request_failed`, nhóm theo `error_type` và chọn `correlation_id`; (3) mở trace cùng ID, kiểm tra observation có trạng thái lỗi.
- Mitigation: tắt scenario lỗi nếu đang practice, khôi phục dependency hỏng và chạy lại smoke test trước khi đóng cảnh báo.

## Alert 3

- Tên: `LowRetrievalSuccessRate`
- Severity: `warning`; duration: `10m`.
- SLI/SLO: tỷ lệ `tool_success=true` trên các sự kiện có kết quả tool; cảnh báo khi thấp hơn `90%` liên tục 10 phút.
- Ảnh hưởng: câu trả lời thiếu context, chất lượng giảm hoặc request thất bại.
- Kiểm tra: (1) xác nhận retrieval success và quality proxy; (2) lọc log có `tool_name=retrieval`, `tool_success=false`; (3) mở trace theo `correlation_id` để kiểm tra lỗi/độ trễ retrieval.
- Mitigation: kiểm tra vector store, timeout và dữ liệu đầu vào; dùng fallback an toàn trong lúc phục hồi rồi xác nhận quality trở lại ngưỡng.
