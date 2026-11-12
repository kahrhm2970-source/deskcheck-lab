# DeskCheck Lab | مختبر الدعم الفني

**الحسين علي أبو طالب — Alhussin Ali Abutalib**

Educational IT Support / Help Desk portfolio built with AI assistance. Synthetic examples; no production deployment or commercial experience implied.

يجمع PowerShell مؤشرات محدودة من Windows، ويحللها Python محليًا لإنتاج تقرير HTML وJSON بالأدلة وخطوات التحقق. يربط المشروع التعامل مع بلاغات البطء وانقطاع الشبكة بتوثيق التشخيص.

## Demo: Python 3.10+ on any OS

No dependencies or account required. Open a terminal in the downloaded/cloned project:

```sh
python deskcheck.py examples/healthy.json --out reports/healthy
python deskcheck.py examples/attention.json --out reports/attention
python -m unittest discover -s tests -v
```

Open `reports/attention/report.html`. Use `python3` or Windows `py -3` if needed.

| Synthetic fixture | Expected findings |
|---|---:|
| healthy.json | 0 |
| attention.json | 5 |

Exit codes: 0 no flags, 1 review needed (reports generated), 2 invalid input/I/O failure. A failed run may leave old reports: check the exit code before opening them.

## Optional Windows collection

Requires Windows PowerShell 5.1+ and NetTCPIP/CIM cmdlets. Read the script first and run only on a computer you are authorized to support:

```powershell
.\Collect-DeskCheck.ps1 -OutFile .\snapshot.json
py -3 deskcheck.py snapshot.json --out reports\local
```

Use your organization's approved script execution process. Do not disable execution policies. Only the output file is written; an existing output file is overwritten. No network probes, remote queries or configuration changes. Collection failures stop the script without writing a new snapshot. Review errors locally as they may contain environment information.

**Validation:** the Python analyzer is tested using synthetic fixtures. The PowerShell collector has not been run against a real Windows workstation in this development session. CI is configured to parse its syntax on Windows; this is not validation of actual device collection.

## Rules

| Code | Trigger | Interpretation |
|---|---|---|
| LOW_MEMORY | free memory below 10% | Point-in-time pressure indicator |
| LOW_DISK | free space below 15% | Review fixed-disk usage |
| APIPA | IPv4 starts 169.254 | Check DHCP path if DHCP expected |
| NO_IPV4 | active interface without IPv4 | IPv6-only may be intentional |
| NO_GATEWAY | no IPv4 gateway | Local-only link may be intentional |
| NO_DNS | no configured DNS addresses | Does not test DNS resolution |
| NO_DISK_DATA / NO_ACTIVE_INTERFACE | empty readings | Review collection scope |

Thresholds are educational heuristics, not Microsoft requirements. Secondary/virtual interfaces are evaluated separately. A flag does not establish a root cause or prove connectivity failure. No automatic repair, cleanup, service restart, IPv6, printer, CPU or patch checks. Zero flags is not proof of device health or security.

## Privacy and input contract

Collector allowlist: percentages and booleans only. No computer name, username, IP, MAC, SSID, serial or raw command output. Analyzer rejects unknown fields and never embeds the original snapshot. Schema version 1 requires exact keys shown in examples, finite percentages from 0–100, strict boolean flags, at most 128 disks/interfaces and files up to 1 MiB. This minimizes data; it is not a general anonymizer.

Keep real reports private and review before sharing. `.gitignore` excludes `snapshot.json` and `reports/`; differently named snapshots require care. Public examples are fictional.

## Interview demo

Explain a slow-device ticket, run the attention fixture (5 findings), explain why APIPA requires verification, compare the healthy fixture (0 findings), then describe the user-approved investigation and escalation. [Arabic runbook](docs/RUNBOOK_AR.md).

## Official references

- [Microsoft Get-NetIPConfiguration](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipconfiguration)
- [Microsoft CIM computer information](https://learn.microsoft.com/en-us/powershell/scripting/samples/collecting-information-about-computers)
- [Python unittest](https://docs.python.org/3/library/unittest.html)

AI assistance was used for implementation, tests and documentation. This is a learning portfolio; real Windows validation is a next step.
