# Persistence via Scheduled Task / Run Key

- **Severity:** High
- **MITRE:** T1053
- **Detection logic:** Windows Event 4698 (scheduled task created) or registry Run key writes
- **Recommended response:** remove persistence, check for related payloads, isolate host if needed
