# Evidence cá nhân

Đặt ảnh hoặc output text dùng để chấm vào thư mục này. Danh sách đầy đủ xem tại [docs/SUBMISSION.md](../../docs/SUBMISSION.md).

Ba output text:

```text
pytest.txt
log-validator.txt
dashboard-validator.txt
```

Năm ảnh runtime tổng hợp theo starter mới:

```text
01-incident-log.png
02-trace-list.png
03-incident-trace.png
04-prompt-versioning.png
05-dashboard-incident.png
```

Trang CP4 trên VLearn vẫn hiển thị checklist evidence `01–14`. Các file tương thích nằm ngay trong thư mục này:

```text
01-pytest.png
02-log-validator.png
03-dashboard-validator.png
04-structured-log.png
05-pii-redaction.png
06-trace-list.png
07-trace-waterfall.png
08-trace-metadata.png
09-prompt-versions.png
10a-prompt-promoted.jpg
10b-prompt-rollback.jpg
11-dashboard-overview.png
12-incident-metric.png
13-incident-log.png
14-incident-trace.png
```

Ảnh 01 lấy từ `data/logs.jsonl`; ảnh 02–04 lấy từ project Langfuse cá nhân; ảnh 05 lấy từ dashboard. Không mở/chụp trang API Keys và không tách thêm ảnh nếu thông tin đã đọc được.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối:

```markdown
![Incident trace](evidence/03-incident-trace.png)
```

Không commit secret, API key, PII thô hoặc evidence của học viên/lớp khác.
