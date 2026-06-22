# safety_checker

A small CLI tool to perform automated, heuristic checks on a webpage.

Features:
- Fetches a URL and reports headers, TLS info, forms, inline scripts, mixed content, robots/sitemap presence.
- `--deep` enumerates links (internal/external counts).
- `--explain` prints short explanations for security-related findings to help learning.
- `--json <file>` writes a JSON report.

Usage:

```bash
python safety_checker.py https://example.com
python safety_checker.py https://example.com --deep --explain
python safety_checker.py https://example.com --json report.json
```

Installation:

```bash
python -m pip install -r requirements.txt
```

License: MIT (see LICENSE)

Interactive menu:

```bash
python safety_checker.py --menu
```

Legal / ethical note:

- This tool performs passive, non-intrusive checks only (HTTP fetches, header analysis, link enumeration). Do not use it for active scanning, fuzzing, or attacks without permission. Always have authorization before running intrusive scans on third-party websites.

Aggressive tests:

- The tool now includes an `--aggressive` mode that can perform directory brute-force checks and basic form injection tests (XSS/SQLi heuristics). These are intrusive and may generate many requests or alter server state. Only run `--aggressive` against systems you own or have explicit permission to test. The interactive menu also exposes these options and will ask for confirmation.
