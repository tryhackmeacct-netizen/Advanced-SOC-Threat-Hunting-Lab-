# PowerShell Abuse (Encoded Download)

- **Severity:** High
- **MITRE:** T1059.001
- **Detection logic:** PowerShell ScriptBlock with `IEX` or encoded payloads that download and execute remote content
- **Recommended response:** quarantine process, retrieve script block, enrich with VT, block remote domain/IP
