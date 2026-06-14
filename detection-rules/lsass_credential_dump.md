# LSASS Credential Dumping

- **Severity:** Critical
- **MITRE:** T1003
- **Detection logic:** Sysmon EventID 10 or abnormal access to lsass.exe
- **Recommended response:** isolate host, collect memory image, block accounts, begin incident response playbook
