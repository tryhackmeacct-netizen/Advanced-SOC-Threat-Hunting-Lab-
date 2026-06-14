# Windows Failed Logon Brute Force

- **Severity:** High
- **MITRE:** T1110 (Brute Force)
- **Detection logic:** multiple 4625 events from same `source.ip` within short timeframe followed by 4624 success
- **Recommended response:** block source IP, review authentication logs, reset affected accounts, initiate incident
