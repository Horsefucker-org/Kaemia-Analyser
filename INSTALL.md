# 🚀 Installation Guide

## ⚡ Quick Start (All Platforms)

### Option 1: Direct Run (Recommended)
```bash
# Linux / macOS
./run.sh https://example.com --aggressive

# Windows
run.bat https://example.com --aggressive
```

### Option 2: Docker (All platforms, no dependencies)
```bash
docker-compose up
# or
docker run -it kaemia/safety-checker --menu
```

### Option 3: Python Package
```bash
pip install safety-checker
safety-checker https://example.com --aggressive
```

---

## 🐧 Linux Installation

### Fedora / Red Hat / CentOS
```bash
git clone https://github.com/Kaemia/safetychecker.git
cd safetychecker
./install.sh
safety-checker https://example.com
```

### Ubuntu / Debian
```bash
git clone https://github.com/Kaemia/safetychecker.git
cd safetychecker
sudo apt-get install python3-pip
./install.sh
safety-checker https://example.com
```

### Arch Linux
```bash
git clone https://github.com/Kaemia/safetychecker.git
cd safetychecker
./install.sh
safety-checker https://example.com
```

---

## 🍎 macOS Installation

### Using Homebrew
```bash
brew tap Kaemia/safety-checker
brew install safety-checker
safety-checker https://example.com
```

### Manual
```bash
git clone https://github.com/Kaemia/safetychecker.git
cd safetychecker
./install.sh
safety-checker https://example.com
```

### Double-click (GUI)
```bash
# Simply double-click run.command in Finder
```

---

## 🪟 Windows Installation

### Method 1: Direct Run
1. Download ZIP from GitHub
2. Extract folder
3. Double-click `run.bat`
4. Enter URL when prompted

### Method 2: Python Package
```cmd
pip install safety-checker
safety-checker https://example.com --aggressive
```

### Method 3: Windows Package Manager (winget)
```cmd
winget install Kaemia.SafetyChecker
safety-checker https://example.com
```

### Method 4: Chocolatey
```cmd
choco install safety-checker
safety-checker https://example.com
```

---

## 🐳 Docker Installation

### Prerequisites
- Docker installed ([get Docker](https://www.docker.com/products/docker-desktop))

### Run
```bash
# Interactive menu
docker-compose up

# Scan specific URL
docker run -it kaemia/safety-checker https://example.com --aggressive

# Save report to file
docker run -it -v $(pwd):/app/reports kaemia/safety-checker \
  https://example.com --json /app/reports/scan.json
```

---

## 📦 Development Installation

```bash
# Clone repo
git clone https://github.com/Kaemia/safetychecker.git
cd safetychecker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Start development
python3 safety_checker.py --menu
```

---

## ✅ Verify Installation

```bash
safety-checker --help
```

Should output usage information.

---

## 🔧 Troubleshooting

### Python not found
- **Linux/macOS**: `sudo apt-get install python3` or `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### pip: command not found
```bash
python3 -m pip install --user safety-checker
```

### Permission denied on run.sh
```bash
chmod +x run.sh
./run.sh
```

### SSL Certificate Error
```bash
# Tool ignores self-signed certificates - this is normal
python3 safety_checker.py https://localhost --aggressive
```

### Timeout Issues
```bash
# Increase timeout
safety-checker https://slow-site.com --timeout 30
```

---

## 🌍 System Requirements

- **Python**: 3.8+
- **Memory**: 256MB minimum
- **Disk**: 50MB minimum
- **Network**: Working internet connection

---

## 📝 Next Steps

- Read [README.md](README.md) for usage guide
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Open [issues](https://github.com/Kaemia/safetychecker/issues) for bugs
