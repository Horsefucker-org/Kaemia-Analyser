#!/usr/bin/env python3
"""
Safety Checker - Comprehensive Website Security Analysis Tool
Aggressive penetration testing methods for maximum coverage
"""

import argparse
import json
import socket
import ssl
import time
import sys
from urllib.parse import urlparse, urljoin, quote
from datetime import datetime
from pathlib import Path
import threading
import random
import string

import requests
from bs4 import BeautifulSoup

# Disable SSL warnings for aggressive testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Rich for clean terminal UI
try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
except Exception:
    Console = None

console = Console() if Console is not None else None

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "curl/7.68.0",
    "Wget/1.20.3",
]

COMMON_DIRS = [
    "admin", "administrator", "wp-admin", "wp-login", "login", "user",
    "api", "api/v1", "api/v2", "api/v3", "rest", "graphql",
    "config", "configuration", "settings", "setup",
    "backup", "sql", "db", "database", ".git", ".env",
    "upload", "uploads", "files", "download", "downloads",
    "tmp", "temp", "cache", "log", "logs",
    "phpmyadmin", "cpanel", "plesk", "panel",
    "xmlrpc.php", "wp-content", "wp-includes",
    "static", "assets", "public", "private",
]

SENSITIVE_FILES = [
    ".git", ".env", ".htaccess", "web.config",
    "config.php", "config.xml", "config.json",
    "database.yml", "secrets.yml",
    "phpinfo.php", "test.php", "debug.php",
    "backup.sql", "dump.sql",
    "robots.txt", "sitemap.xml",
]

XSS_PAYLOADS = [
    '<script>alert("xss")</script>',
    '"><script>alert("xss")</script>',
    "'-alert(1)-'",
    '<img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
    'javascript:alert(1)',
]

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR 1=1/*",
    "admin' --",
    "' UNION SELECT NULL--",
    "1' AND '1'='1",
]

HEADERS_TO_TEST = [
    "x-frame-options",
    "content-security-policy",
    "strict-transport-security",
    "x-content-type-options",
    "x-xss-protection",
    "referrer-policy",
    "permissions-policy",
    "access-control-allow-origin",
    "cache-control",
]


def get_random_user_agent():
    return random.choice(USER_AGENTS)


def fetch(url, timeout=10, verify=False):
    """Fetch URL with custom headers"""
    try:
        headers = {"User-Agent": get_random_user_agent()}
        start = time.time()
        r = requests.get(url, timeout=timeout, allow_redirects=True, 
                        headers=headers, verify=verify)
        elapsed = time.time() - start
        return r, elapsed
    except requests.RequestException as e:
        return {"error": str(e)}, None


def check_headers(resp):
    """Check security headers"""
    headers = {k.lower(): v for k, v in resp.headers.items()}
    missing_headers = []
    weak_headers = []
    
    for header in HEADERS_TO_TEST:
        if header not in headers:
            missing_headers.append(header)
        else:
            val = headers[header]
            if "unsafe" in val.lower() or val.lower() == "none":
                weak_headers.append({header: val})
    
    return {
        "present": {k: headers.get(k) for k in HEADERS_TO_TEST if k in headers},
        "missing": missing_headers,
        "weak": weak_headers,
        "server": headers.get("server", "Unknown"),
        "powered_by": headers.get("x-powered-by", "Not disclosed"),
    }


def check_tls_cert(hostname, port=443, timeout=5):
    """Check TLS certificate details"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                return {
                    "version": version,
                    "cipher": cipher[0] if cipher else "Unknown",
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "subject": dict(x[0] for x in cert.get("subject", [])),
                    "notAfter": cert.get("notAfter"),
                }
    except Exception as e:
        return {"error": str(e)}


def parse_forms(soup):
    """Extract all forms from page"""
    forms = []
    for form in soup.find_all("form"):
        inputs = []
        for inp in form.find_all(["input", "textarea", "select"]):
            inputs.append({
                "name": inp.get("name"),
                "type": inp.get("type", "text"),
                "value": inp.get("value", "")
            })
        forms.append({
            "action": form.get("action", ""),
            "method": (form.get("method") or "GET").upper(),
            "inputs": inputs,
            "has_password": any(i["type"].lower() == "password" for i in inputs),
        })
    return forms


def check_robots(base_url):
    """Check robots.txt"""
    u = urlparse(base_url)
    robots_url = f"{u.scheme}://{u.netloc}/robots.txt"
    try:
        r = requests.get(robots_url, timeout=5, headers={"User-Agent": get_random_user_agent()})
        if r.status_code == 200:
            return {"exists": True, "content": r.text[:500]}
        return {"exists": False}
    except:
        return {"exists": False}


def check_sitemap(base_url):
    """Check sitemap.xml"""
    u = urlparse(base_url)
    sitemap_url = f"{u.scheme}://{u.netloc}/sitemap.xml"
    try:
        r = requests.get(sitemap_url, timeout=5, headers={"User-Agent": get_random_user_agent()})
        if r.status_code == 200:
            return {"exists": True, "urls_count": len(r.text.split("<loc>"))}
        return {"exists": False}
    except:
        return {"exists": False}


def dir_brute_force(base_url, timeout=10, max_threads=10):
    """Aggressive directory bruteforce"""
    u = urlparse(base_url)
    base = f"{u.scheme}://{u.netloc}"
    found = []
    lock = threading.Lock()
    
    def check_dir(path):
        try:
            full_url = f"{base}/{path}"
            headers = {"User-Agent": get_random_user_agent()}
            r = requests.get(full_url, timeout=3, headers=headers, verify=False)
            if r.status_code in [200, 301, 302, 403]:
                with lock:
                    found.append({"path": path, "status": r.status_code})
        except:
            pass
    
    threads = []
    for path in COMMON_DIRS:
        t = threading.Thread(target=check_dir, args=(path,))
        threads.append(t)
        t.start()
        if len(threads) >= max_threads:
            for t in threads:
                t.join()
            threads = []
    
    for t in threads:
        t.join()
    
    return found


def test_xss_injection(base_url, forms):
    """Test for XSS vulnerabilities"""
    u = urlparse(base_url)
    base = f"{u.scheme}://{u.netloc}"
    vulns = []
    
    for form in forms:
        action = form.get("action", "")
        if not action:
            continue
        
        action_url = urljoin(base_url, action)
        method = form.get("method", "GET")
        
        for payload in XSS_PAYLOADS:
            try:
                data = {inp["name"]: payload for inp in form["inputs"] if inp["name"]}
                if not data:
                    continue
                
                if method.upper() == "POST":
                    r = requests.post(action_url, data=data, timeout=5, verify=False)
                else:
                    r = requests.get(action_url, params=data, timeout=5, verify=False)
                
                if payload in r.text:
                    vulns.append({
                        "type": "Reflected XSS",
                        "form": action,
                        "payload": payload,
                        "method": method
                    })
            except:
                pass
    
    return vulns


def test_sqli_injection(base_url, forms):
    """Test for SQL Injection vulnerabilities"""
    vulns = []
    
    for form in forms:
        action = form.get("action", "")
        if not action:
            continue
        
        action_url = urljoin(base_url, action)
        method = form.get("method", "GET")
        
        for payload in SQLI_PAYLOADS:
            try:
                data = {inp["name"]: payload for inp in form["inputs"] if inp["name"]}
                if not data:
                    continue
                
                if method.upper() == "POST":
                    r = requests.post(action_url, data=data, timeout=5, verify=False)
                else:
                    r = requests.get(action_url, params=data, timeout=5, verify=False)
                
                # Check for SQL error indicators
                error_indicators = ["sql", "syntax", "mysql", "postgresql", "database error"]
                if any(ind in r.text.lower() for ind in error_indicators):
                    vulns.append({
                        "type": "SQL Error Detected",
                        "form": action,
                        "payload": payload,
                        "method": method
                    })
            except:
                pass
    
    return vulns


def check_open_redirects(base_url, forms):
    """Check for open redirect vulnerabilities"""
    redirect_url = "https://evil.com"
    vulns = []
    
    for form in forms:
        action = form.get("action", "")
        if not action:
            continue
        
        for inp in form["inputs"]:
            if any(x in inp["name"].lower() for x in ["redirect", "url", "next", "return", "target"]):
                try:
                    data = {inp["name"]: redirect_url}
                    r = requests.post(urljoin(base_url, action), data=data, 
                                    timeout=5, allow_redirects=False, verify=False)
                    if redirect_url in r.headers.get("location", ""):
                        vulns.append({
                            "type": "Open Redirect",
                            "parameter": inp["name"],
                            "payload": redirect_url
                        })
                except:
                    pass
    
    return vulns


def enumerate_links(soup, base_url):
    """Enumerate all links"""
    internal = set()
    external = set()
    parsed_base = urlparse(base_url).netloc
    
    for link in soup.find_all("a", href=True):
        href = urljoin(base_url, link.get("href"))
        try:
            if urlparse(href).netloc == parsed_base:
                internal.add(href)
            else:
                external.add(href)
        except:
            pass
    
    return {"internal_count": len(internal), "external_count": len(external), "internal": list(internal)[:50]}


def test_cors(base_url):
    """Test CORS misconfiguration"""
    headers = {"User-Agent": get_random_user_agent(), "Origin": "https://attacker.com"}
    try:
        r = requests.get(base_url, headers=headers, timeout=5, verify=False)
        cors_origin = r.headers.get("access-control-allow-origin", "")
        cors_creds = r.headers.get("access-control-allow-credentials", "")
        
        if cors_origin and (cors_origin == "*" or cors_origin == "https://attacker.com"):
            return {
                "vulnerable": True,
                "allow_origin": cors_origin,
                "allow_credentials": cors_creds
            }
        return {"vulnerable": False}
    except:
        return {"error": "Could not test CORS"}


def test_default_credentials(base_url):
    """Test common default credentials"""
    defaults = [
        ("admin", "admin"),
        ("admin", "password"),
        ("test", "test"),
        ("root", "root"),
    ]
    
    found = []
    for user, pwd in defaults:
        try:
            r = requests.post(base_url, data={"username": user, "password": pwd}, 
                            timeout=5, verify=False)
            if r.status_code == 200 and "success" in r.text.lower():
                found.append({"username": user, "password": pwd})
        except:
            pass
    
    return found


def run_all_checks(url, deep=False, aggressive=False, timeout=10):
    """Run all security checks"""
    result = {"url": url, "timestamp": datetime.now().isoformat()}
    
    try:
        resp, elapsed = fetch(url, timeout=timeout)
        if isinstance(resp, dict) and "error" in resp:
            result["error"] = resp["error"]
            return result
        
        result["response_time"] = elapsed
        result["status_code"] = resp.status_code
        result["final_url"] = resp.url
        
        # Basic checks
        result["headers"] = check_headers(resp)
        
        hostname = urlparse(url).netloc
        result["tls"] = check_tls_cert(hostname, timeout=timeout)
        
        result["robots"] = check_robots(url)
        result["sitemap"] = check_sitemap(url)
        
        # Parse content
        soup = BeautifulSoup(resp.text, "html.parser")
        result["forms"] = parse_forms(soup)
        
        if deep:
            result["links"] = enumerate_links(soup, url)
            result["cors"] = test_cors(url)
        
        if aggressive:
            result["directories"] = dir_brute_force(url, timeout=timeout)
            result["xss_tests"] = test_xss_injection(url, result["forms"])
            result["sqli_tests"] = test_sqli_injection(url, result["forms"])
            result["open_redirects"] = check_open_redirects(url, result["forms"])
            result["default_creds"] = test_default_credentials(url)
        
        return result
    
    except Exception as e:
        result["error"] = str(e)
        return result


def print_report(report, explain=False, json_out=None):
    """Print security report"""
    if json_out:
        with open(json_out, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {json_out}")
        return
    
    print("\n" + "="*70)
    print(f"SECURITY REPORT: {report.get('url')}")
    print("="*70)
    
    if "error" in report:
        print(f"ERROR: {report['error']}")
        return
    
    print(f"\nStatus Code: {report.get('status_code')}")
    print(f"Response Time: {report.get('response_time'):.2f}s")
    
    # Headers
    headers = report.get("headers", {})
    print("\n[HEADERS]")
    print(f"Server: {headers.get('server', 'Unknown')}")
    print(f"Missing Security Headers: {', '.join(headers.get('missing', []))}")
    if headers.get('weak'):
        print(f"Weak Headers: {headers.get('weak')}")
    
    # TLS
    tls = report.get("tls", {})
    if "error" not in tls:
        print(f"\n[TLS]")
        print(f"Version: {tls.get('version', 'Unknown')}")
        print(f"Cipher: {tls.get('cipher', 'Unknown')}")
    
    # Forms
    forms = report.get("forms", [])
    if forms:
        print(f"\n[FORMS] Found {len(forms)} form(s)")
    
    # Aggressive results
    if report.get("directories"):
        print(f"\n[DIRECTORIES FOUND]")
        for d in report["directories"]:
            print(f"  {d['path']} ({d['status']})")
    
    if report.get("xss_tests"):
        print(f"\n[XSS VULNERABILITIES]")
        for v in report["xss_tests"]:
            print(f"  {v['type']} in {v['form']}")
    
    if report.get("sqli_tests"):
        print(f"\n[SQL INJECTION TESTS]")
        for v in report["sqli_tests"]:
            print(f"  {v['type']} in {v['form']}")
    
    if report.get("cors", {}).get("vulnerable"):
        print(f"\n[CORS MISCONFIGURATION]")
        print(f"  Allow-Origin: {report['cors'].get('allow_origin')}")


def interactive_menu():
    """Interactive menu using Rich for a clean UI if available."""
    if console is None:
        # Fallback to simple CLI if Rich is not installed
        while True:
            print("\n" + "=" * 60)
            print("SAFETY CHECKER - Interactive Mode")
            print("=" * 60)
            print("1. Basic scan (passive)")
            print("2. Deep scan (link enumeration)")
            print("3. Aggressive scan (directory brute-force, XSS, SQLi tests)")
            print("4. Full scan (everything)")
            print("5. Exit")

            choice = input("Choose option (1-5): ").strip()

            if choice == "5":
                break
            elif choice in ["1", "2", "3", "4"]:
                url = input("Enter URL (e.g., https://example.com): ").strip()
                if not url.startswith("http"):
                    url = "https://" + url

                deep = choice in ["2", "4"]
                aggressive = choice in ["3", "4"]

                if aggressive:
                    confirm = input("Aggressive tests will make many requests. Continue? (yes/no): ").strip()
                    if confirm.lower() not in ["yes", "y"]:
                        print("Cancelled")
                        continue

                print("Running scan...")
                report = run_all_checks(url, deep=deep, aggressive=aggressive)
                print_report(report, explain=True)
    else:
        while True:
            console.rule("SAFETY CHECKER - Interactive Mode")
            console.print("[1] Basic scan (passive)  [2] Deep scan (links)  [3] Aggressive scan  [4] Full scan  [5] Exit", style="bold cyan")
            try:
                choice = Prompt.ask("Choose option", choices=["1", "2", "3", "4", "5"], default="1")
            except Exception:
                choice = "1"

            if choice == "5":
                console.print("Goodbye", style="green")
                break

            url = Prompt.ask("Enter URL (e.g., https://example.com)")
            if not url.startswith("http"):
                url = "https://" + url

            deep = choice in ["2", "4"]
            aggressive = choice in ["3", "4"]

            if aggressive:
                ok = Confirm.ask("Aggressive tests will make many requests and may trigger alerts. Continue?", default=False)
                if not ok:
                    console.print("Cancelled", style="yellow")
                    continue

            console.print(Panel.fit(f"Running scan for: {url}\nDeep: {deep}  Aggressive: {aggressive}", title="Scanning", subtitle="Please wait..."))
            with console.status("Running checks…", spinner="dots"):
                report = run_all_checks(url, deep=deep, aggressive=aggressive)

            # Present results
            if report.get("error"):
                console.print(f"[red]Error:[/red] {report['error']}")
            else:
                console.rule("Scan Results")
                # Headers summary
                headers = report.get("headers", {})
                missing = headers.get("missing", [])
                console.print(f"Server: {headers.get('server', 'Unknown')}")
                console.print(f"Missing Security Headers: {', '.join(missing) if missing else 'None'}")

                if report.get("directories"):
                    console.print(Panel.fit(str(report.get("directories")[:10]), title="Directories found"))

                if report.get("xss_tests"):
                    console.print(Panel.fit(str(report.get("xss_tests")), title="XSS Findings", style="red"))

                if report.get("sqli_tests"):
                    console.print(Panel.fit(str(report.get("sqli_tests")), title="SQLi Findings", style="red"))

                # Offer JSON export
                if Confirm.ask("Save full report to JSON file?", default=False):
                    fname = Prompt.ask("Filename", default=f"scan_{int(time.time())}.json")
                    try:
                        with open(fname, "w") as fh:
                            json.dump(report, fh, indent=2)
                        console.print(f"Saved report to [green]{fname}[/green]")
                    except Exception as e:
                        console.print(f"Failed to save report: {e}", style="red")



def main():
    parser = argparse.ArgumentParser(
        description="Safety Checker - Website Security Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 safety_checker.py https://example.com
  python3 safety_checker.py https://example.com --deep --aggressive
  python3 safety_checker.py https://example.com --json report.json
        """
    )
    
    parser.add_argument("url", nargs="?", help="URL to scan")
    parser.add_argument("--deep", action="store_true", help="Deep scan (enumerate links)")
    parser.add_argument("--aggressive", action="store_true", help="Aggressive scan (brute-force, injection tests)")
    parser.add_argument("--json", help="Output JSON report to file")
    parser.add_argument("--menu", action="store_true", help="Interactive menu mode")
    parser.add_argument("--timeout", type=float, default=10, help="Request timeout (default: 10s)")
    
    args = parser.parse_args()
    
    if args.menu or not args.url:
        interactive_menu()
    else:
        report = run_all_checks(args.url, deep=args.deep, aggressive=args.aggressive, timeout=args.timeout)
        print_report(report, json_out=args.json)


if __name__ == "__main__":
    main()
