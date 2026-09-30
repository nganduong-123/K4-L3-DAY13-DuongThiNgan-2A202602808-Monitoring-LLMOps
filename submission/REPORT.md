# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Bộ evidence giữ cả checklist `01–14` đang hiển thị trên VLearn và bộ 5 ảnh tổng hợp trong starter mới; mọi đường dẫn đều là đường dẫn tương đối.

## 1. Thông tin học viên

- **Họ và tên:** Dương Thị Ngân
- **MSSV:** 2A202602808
- **Lớp:** K4-L3B
- **Repository URL:** `https://github.com/nganduong-123/K4-L3-DAY13-DuongThiNgan-2A202602808-Monitoring-LLMOps`
- **Commit SHA nộp:** xem SHA được ghi cùng URL trên VLearn
- **Challenge chính thức:** `day13-k4-l3b-monitoring-llmops-v1`, lấy từ commit phát hành chính thức `0a7eadb` của repo đề K4-L3B
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602808`

## 2. Evidence index

Ba output text và năm ảnh tổng hợp theo starter mới:

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/pytest.txt` |
| Log validator | `evidence/log-validator.txt` |
| Dashboard validator | `evidence/dashboard-validator.txt` |
| Structured log + incident log | `evidence/01-incident-log.png` |
| Trace list | `evidence/02-trace-list.png` |
| Trace waterfall + metadata + incident trace | `evidence/03-incident-trace.png` |
| Prompt versions + promote/rollback | `evidence/04-prompt-versioning.png` |
| Dashboard + incident metric | `evidence/05-dashboard-incident.png` |

Checklist evidence `01–14` theo trang CP4 trên VLearn:

| # | Đường dẫn | Nội dung chính |
|---:|---|---|
| 01 | `evidence/01-pytest.png` | Commit code và pytest pass |
| 02 | `evidence/02-log-validator.png` | Log validator 100/100 |
| 03 | `evidence/03-dashboard-validator.png` | Dashboard validator 6/6 |
| 04 | `evidence/04-structured-log.png` | Request/response JSON cùng `correlation_id=req-dbd2aee3` |
| 05 | `evidence/05-pii-redaction.png` | Email, phone, CCCD và thẻ đều được che |
| 06 | `evidence/06-trace-list.png` | Project cá nhân và danh sách trace |
| 07 | `evidence/07-trace-waterfall.png` | Cây root → retrieval + generation |
| 08 | `evidence/08-trace-metadata.png` | Metadata cùng request với ảnh 04 |
| 09 | `evidence/09-prompt-versions.png` | Prompt v1/v2 và labels |
| 10a | `evidence/10a-prompt-promoted.jpg` | `production` được promote sang v2 |
| 10b | `evidence/10b-prompt-rollback.jpg` | `production` rollback về v1 |
| 11 | `evidence/11-dashboard-overview.png` | Dashboard đủ 6 panel |
| 12 | `evidence/12-incident-metric.png` | Metric bất thường sau challenge |
| 13 | `evidence/13-incident-log.png` | Incident log `req-dbd2aee3`, latency 2671 ms |
| 14 | `evidence/14-incident-trace.png` | Incident trace cùng correlation ID, retrieval 2.50 s |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---:|---:|---|
| `validate_logs.py` | 30/100 theo trạng thái starter có TODO | 100/100 | Đủ schema, enrichment, correlation ID, không PII thô |
| `validate_dashboard.py` | 6/6 contract | 6/6 | Dashboard runtime đọc trực tiếp `data/logs.jsonl` |
| `pytest` | Chưa chạy trước khi sửa TODO | 22 passed | Python 3.11 |
| Số traces hợp lệ | 0 | 47 trace gốc / 141 observations | Mỗi trace có agent, retrieval, generation |
| Số PII leak | Có nguy cơ do scrubber chưa đăng ký | 0 | Validator độc lập xác nhận |
| Latency P50 / P95 / P99 | Chưa có dữ liệu | 156 / 2671 / 2671 ms | Cửa sổ dashboard 60 phút vẫn chứa workload CP3 chính thức và các request phục hồi |
| TTFT P95 | Chưa có dữ liệu | 53 ms | Fake LLM; thấp hơn nhiều so với độ trễ retrieval |
| Retrieval success rate | Chưa có dữ liệu | 100% | Challenge làm retrieval chậm nhưng không làm tool fail |

## 4. Logging và PII

- Middleware xóa context cũ, nhận `x-request-id` hợp lệ hoặc sinh `req-<8-hex>`, bind vào `structlog`, lưu vào `request.state` và trả lại trong header `x-request-id`; `x-response-time-ms` chứa thời gian xử lý.
- Trước `request_received`, log được enrich bằng `user_id_hash`, `session_id`, `feature`, `model`, `env`; response còn có latency, TTFT, token, cost, quality và kết quả retrieval.
- `scrub_event` chạy trước file writer/JSON renderer và scrub đệ quy mọi chuỗi trong dict/list/tuple. Pattern che email, số điện thoại Việt Nam, CCCD, thẻ thanh toán, hộ chiếu và địa chỉ phổ biến.
- Kiểm chứng bằng `scripts/validate_logs.py` và các input có email, điện thoại, thẻ. Kết quả cuối: 118 record, 60 correlation ID, 0 PII leak, 100/100.

## 5. Tracing và prompt versioning

- Project Langfuse thuộc tài khoản cá nhân, tên đúng `day13-k4-l3b-2A202602808`; ảnh không mở trang API Keys.
- Cây observation: `day13-agent-request → lab-agent-run → retrieval + generation`. Retrieval ghi query/doc preview đã scrub; generation ghi model, prompt version, input/output token và cost, không capture raw PII.
- Log và trace nối bằng `metadata.correlation_id`. Ví dụ candidate trace có `correlation_id=req-ca8d1da2`.
- Prompt name: `day13-chat`.
- Version 1: labels `baseline`, `production`; version 2: label `candidate`.
- Trace version 1: `98181e45ab8e66a4f57ac05fa2cb777e`; trace candidate version 2: `98d61bc9e906d98faecc506c2192daa0`; trace production version 2: `20f056d7871f60340f836f74fa22d733`.
- Đã promote `production` sang version 2, chạy request kiểm tra, sau đó rollback `production` về version 1. Trạng thái cuối: v1=`baseline+production`, v2=`candidate`.

## 6. Dashboard, SLO và alerts

- Dashboard runtime có đúng 6 panel: latency/TTFT, traffic, errors/retrieval success, cost, tokens, quality. Nguồn là `data/logs.jsonl`, time range 60 phút, refresh 30 giây, hiện đơn vị và threshold.
- SLO chính: 99.5% request có `response_sent` và latency không quá 3000 ms trong 28 ngày.
- Error budget là 0.5%; nếu có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng.
- Ba alert symptom-based: `HighLatencyP95`, `HighRequestErrorRate`, `LowRetrievalSuccessRate`; mỗi alert có severity, duration, Slack channel, owner và runbook trong `docs/alerts.md`.

## 7. Điều tra incident CP3 chính thức

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`.
- **Khoảng thời gian:** 2026-09-30 11:23–11:24 (Asia/Ho_Chi_Minh).
- **Triệu chứng từ metrics:** latency P50/P95/P99 là 156/2671/2671 ms trong cửa sổ gồm cả incident và request phục hồi; error rate vẫn 0% và retrieval success 100%.
- **Log line:** `response_sent`, `correlation_id=req-dbd2aee3`, `latency_ms=2671`, `tool_name=retrieval`, `tool_success=true`.
- **Trace:** `a09b010ee64003227900b922c6bd2b07`; root `lab-agent-run` khoảng 2.68 s, retrieval span 2.50 s, generation span khoảng 0.15 s.
- **Root cause:** challenge bật `rag_slow`, độ trễ nằm ở retrieval; generation, model và tool result không lỗi.
- **Fix action:** tắt incident `rag_slow`; 10 request kiểm tra sau đó đều HTTP 200 và phục hồi về khoảng 163–219 ms.
- **Preventive measure:** alert P95, timeout/circuit breaker cho retrieval, cache kết quả phù hợp và luôn nối metric → log → trace bằng `correlation_id`.

## 8. Giải thích và tự đánh giá

- Quyết định quan trọng nhất là chỉ lưu preview đã scrub trong cả log và trace, vẫn đủ quan sát nhưng không làm lộ input người dùng.
- Blocker gặp phải: port 8000 đang được dịch vụ Day 12 sử dụng. Tôi bổ sung `--base-url` cho hai script để chạy Day 13 tại port 8013 mà không dừng dịch vụ khác.
- Luồng điều tra: Metrics khoanh vùng triệu chứng/thời gian → Logs chọn đúng request bằng correlation ID → Traces chỉ ra span retrieval chậm → xác nhận root cause.
- Prompt labels giúp đổi version không cần deploy code; token/cost cho biết prompt có làm chi phí tăng; SLO/alert giúp phát hiện tác động; rollback đưa production về phiên bản ổn định.
- Điều học được: observability chỉ hữu ích khi metrics, logs và traces dùng chung metadata và evidence có thể truy ngược tới cùng một request.
- File `config/challenge.json` chính thức lấy nguyên vẹn từ starter K4-L3B đã được dùng để chạy CP3 và không bị tự ý sửa/thay thế.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Có đúng 3 file text và 5 ảnh runtime theo hướng dẫn.
- [x] Có đủ checklist evidence `01–14` theo trang CP4 trên VLearn.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
