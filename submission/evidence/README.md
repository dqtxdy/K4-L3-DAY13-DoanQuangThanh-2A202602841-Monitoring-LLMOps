# Evidence cá nhân

Đặt ảnh hoặc output text dùng để chấm vào thư mục này. Danh sách đầy đủ xem tại [docs/SUBMISSION.md](../../docs/SUBMISSION.md).

Tên file gợi ý:

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
10-prompt-rollback-before.png
10-prompt-rollback-after.png
11-dashboard-overview.png
12-incident-metric.png
13-incident-log.png
14-incident-trace.png
```

Có thể dùng `.txt` cho output của tests/validators. Có thể tách dashboard thành nhiều ảnh nếu một ảnh không đọc rõ.

Ảnh `04`, `05`, `13` lấy từ terminal hoặc `data/logs.jsonl`. Ảnh `06`–`10`, `14` lấy từ project Langfuse cá nhân `day13-k4-l3b-<MSSV>` và nên nhìn thấy tên project. Không mở/chụp trang API Keys.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.png)
```

Không commit secret, API key, PII thô hoặc evidence của học viên/lớp khác.

## Runtime outputs captured

The following files contain actual local test/log output or records queried from this repository's configured Langfuse project. They are text/data exports, not screenshots:

```text
01-pytest.txt
02-log-validator.txt
03-dashboard-validator.txt
04-structured-log.jsonl
05-pii-redaction.txt
06-trace-list.txt
07-trace-waterfall.txt
08-trace-metadata.txt
09-prompt-versions.txt
10-prompt-rollback.txt
11-dashboard-runtime.txt
12-incident-metric.txt
13-incident-log.jsonl
14-incident-trace.txt
15-incident-recovery.txt
```

Screenshots currently present: `04-structured-log.png`, `05-pii-redaction.png`, `06-trace-list.png`, `07-trace-waterfall.png`, `08-trace-metadata.png`, `09-prompt-versions.png`, both `10-prompt-rollback-*.png` states, `11-dashboard-overview.png`, and incident screenshots `12-incident-metric.png`, `13-incident-log.png`, `14-incident-trace.png`. Screenshot 06 has an opaque mask over the account area; screenshot 08 has an opaque mask over the `scope.attributes.public_key` value. The rest of each screenshot is preserved. Screenshots 07/09/10 are the latest user captures and show the personal project context. Screenshot 04 remains small and could be retaken at larger zoom.

Langfuse and dashboard screenshots 04–11 are present. Official challenge runtime text evidence 12–15 is captured. Screenshots 12 and 14 are saved; screenshot 13 is saved at 5054 × 406; open it at full resolution to read the JSON line. Screenshot 14 has the visible public-key value masked. The project title is `day13-k4-l3b-2A202602841`; no API keys page is included. Incident trace text excludes input/output previews and resource-level key attributes.
