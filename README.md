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

Quick install for users (Fedora / Linux)

You can run the included installer which prefers `pipx` (recommended) and falls back to a `pip --user` install. Run from the repo root after cloning:

```bash
./install.sh
# or force user-mode:
./install.sh --method user
```

After install you can call the CLI directly as `safety-checker`:

```bash
safety-checker https://example.com --deep --explain
```

If you plan to publish this repo on GitHub, users will be able to clone and run `./install.sh` or use `pipx install <github-user>/safetychecker` once the package is published.
