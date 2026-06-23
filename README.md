# 🛡️ Safety Checker - Website Security Scanner

**Professional Website Security Analysis & Penetration Testing Tool with Aggressive Hacker Methods**

Scan websites for security vulnerabilities: XSS, SQLi, weak headers, CORS misconfigurations, open redirects, and more.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)

---

## ⚡ Quick Start (2 minutes)

### 1️⃣ Clone & Run (All Platforms)
```bash
git clone https://github.com/Horsefucker-org/Kaemia-Analyser.git
cd Kaemia-Analyser
./run.sh          # Linux/macOS
# or
run.bat           # Windows (double-click or run in Command Prompt)
```

### 2️⃣ Enter Your Website URL
The **interactive menu** opens automatically:
```
═══════════════════════════════════════
SAFETY CHECKER - Interactive Mode
═══════════════════════════════════════
1. Basic scan (passive)
2. Deep scan (link enumeration)
3. Aggressive scan (directory brute-force, XSS, SQLi tests)
4. Full scan (everything)
5. Exit

Choose option (1-5): 3
Enter URL (e.g., https://example.com): https://your-website.com
Aggressive tests will make many requests. Continue? (yes/no): yes
Running scan...
```

### 3️⃣ View Results
```
[HEADERS]
Server: nginx
Missing Security Headers: x-frame-options, content-security-policy

[DIRECTORIES FOUND]
  admin (403)
  api (200)

[XSS VULNERABILITIES]
  Reflected XSS in /search?q=

[SQL INJECTION TESTS]
  SQL Error Detected in /login
```

---

## 🎯 Usage Modes

### 📌 Interactive Menu (Recommended - Just run it!)
```bash
./run.sh          # Automatically opens interactive menu
```
Enter your website URL and choose scan type. That's it!

### 🖥️ Command Line (For Scripting)
```bash
# Basic scan
./run.sh https://example.com

# Deep scan (enumerate links)
./run.sh https://example.com --deep

# Aggressive scan (XSS, SQLi, Directory Brute-Force)
./run.sh https://example.com --aggressive

# Full scan (everything)
./run.sh https://example.com --deep --aggressive

# Save to JSON file
./run.sh https://example.com --aggressive --json report.json

# Custom timeout (for slow websites)
./run.sh https://example.com --timeout 30
```

---

## Features

### Passive Analysis
- 🔍 **Security Headers Analysis** - Detects missing/weak security headers
- 🔐 **TLS/SSL Certificate Inspection** - Full certificate chain analysis
- 📋 **Form Detection** - Identifies all forms and input fields
- 🤖 **robots.txt & sitemap.xml** - Checks for information disclosure
- 🔗 **Link Enumeration** - Maps internal/external links

### Aggressive Testing (Hacker Methods)
- 💥 **Directory Brute-Force** - Multi-threaded directory enumeration
- 💉 **XSS Injection Testing** - Reflected XSS vulnerability detection
- 🗄️ **SQL Injection Testing** - SQLi vulnerability detection
- 🔄 **CORS Misconfiguration** - Identifies CORS bypass vectors
- 🚪 **Open Redirect Detection** - Finds redirect vulnerabilities
- 🔑 **Default Credentials Testing** - Tests common default login credentials

### Advanced Options
- 📊 **JSON Export** - Structured reporting for automation
- ⏱️ **Custom Timeouts** - Adaptive network handling
- 🎯 **Interactive Menu** - User-friendly scan wizard
- 📈 **Detailed Reporting** - Comprehensive vulnerability summaries

## Installation

### Quick Start (Linux/Fedora)
```bash
git clone https://github.com/Kaemia/safetychecker.git
cd safetychecker
./run.sh
```

### Automated Install
```bash
./install.sh
```

After installation:
```bash
safety-checker https://example.com --aggressive
```

### Manual Installation
```bash
pip install -r requirements.txt
python3 safety_checker.py --help
```

## Usage

### Interactive Mode (Recommended)
```bash
./run.sh
```
or
```bash
python3 safety_checker.py --menu
```

### Command Line - Basic Scan
```bash
python3 safety_checker.py https://example.com
```

### Command Line - Deep Scan (Link Enumeration)
```bash
python3 safety_checker.py https://example.com --deep
```

### Command Line - Aggressive Scan (Full Pentesting)
```bash
python3 safety_checker.py https://example.com --aggressive
```

### Command Line - Full Suite
```bash
python3 safety_checker.py https://example.com --deep --aggressive --timeout 15
```

### JSON Report Output
```bash
python3 safety_checker.py https://example.com --aggressive --json report.json
```

## Examples

**Test own domain with all checks:**
```bash
safety-checker https://mysite.com --deep --aggressive --json scan_report.json
```

**Quick security audit:**
```bash
safety-checker https://company.com --deep
```

**Penetration testing with extended timeout:**
```bash
safety-checker https://target.com --aggressive --timeout 30
```

## Output

### Standard Output
```
======================================================================
SECURITY REPORT: https://example.com
======================================================================
Status Code: 200
Response Time: 1.23s

[HEADERS]
Server: nginx/1.24.0
Missing Security Headers: x-frame-options, content-security-policy

[TLS]
Version: TLSv1.3
Cipher: TLS_AES_256_GCM_SHA384

[DIRECTORIES FOUND]
  admin (403)
  api (200)
  config (403)

[XSS VULNERABILITIES]
  Reflected XSS in /search?q=

[SQL INJECTION TESTS]
  SQL Error Detected in /login
```

### JSON Report
Structured JSON output for integration with security tools and dashboards.

## Warning ⚠️

**⚠️ Legal & Ethical Notice:**

- This tool is designed for authorized security testing ONLY
- Only use on websites/systems you own or have explicit permission to test
- Unauthorized testing is illegal and may violate the Computer Fraud and Abuse Act
- The author is not responsible for misuse
- Always get written authorization before testing third-party systems

The `--aggressive` flag performs intrusive testing that may:
- Generate many HTTP requests
- Trigger security alerts
- Potentially disrupt service
- Be flagged by WAF/IDS systems

## Requirements

- Python 3.8+
- requests
- beautifulsoup4
- urllib3

## Development

### Setup Development Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest tests/
pytest --cov=safety_checker tests/
```

### Code Quality
```bash
black safety_checker.py
isort safety_checker.py
flake8 safety_checker.py
```

## Project Structure
```
safetychecker/
├── safety_checker.py       # Main application
├── requirements.txt        # Dependencies
├── pyproject.toml          # Package configuration
├── README.md              # This file
├── LICENSE                # MIT License
├── run.sh                 # Quick start script
├── install.sh             # Installation script
├── .gitignore            # Git ignore rules
├── tests/                # Unit tests
│   └── test_safety_checker.py
├── wordlists/            # Brute-force dictionaries
└── .github/workflows/    # CI/CD automation
    └── tests.yml
```

## Performance Tips

1. **Adjust Timeout**: Use `--timeout 20` for slow sites
2. **Reduce Threads**: Directory brute-force uses 10 threads by default
3. **Target Specific Tests**: Run basic scan first, then aggressive if needed
4. **Use JSON Export**: For batch processing of results

## Troubleshooting

**SSL Certificate Error:**
```bash
# The tool ignores self-signed certificates in aggressive mode
python3 safety_checker.py https://localhost --aggressive
```

**Timeout Issues:**
```bash
# Increase timeout for slow responses
python3 safety_checker.py https://slow-site.com --timeout 30
```

**Permission Denied (run.sh):**
```bash
chmod +x run.sh
./run.sh
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Future Roadmap

- [ ] GUI Desktop Application (PyQt)
- [ ] Electron-based UI
- [ ] Real-time scan dashboard
- [ ] WebSocket support testing
- [ ] API vulnerability detection
- [ ] Advanced payload libraries
- [ ] Multi-threading optimization
- [ ] Plugin system
- [ ] Cloud scan capability
- [ ] Mobile app

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is provided "as-is" for educational and authorized testing purposes. Unauthorized access to computer systems is illegal. The authors assume no liability for misuse.

---

**Made with ❤️ for security professionals**

Need help? Open an issue on [GitHub](https://github.com/Kaemia/safetychecker/issues)
