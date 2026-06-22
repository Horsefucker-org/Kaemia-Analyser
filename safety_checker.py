"""Comprehensive webpage analysis tool.

Features:
- automatic checks (headers, forms, inline scripts, links, robots/sitemap, TLS)
- JSON output to console/file
- `--explain` to include short explanations of findings (helpful for learning)
- `--deep` option to include link enumeration and counts
"""

import argparse
import json
import socket
import ssl
import time
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


SECURITY_HEADER_EXPLANATIONS = {
    "x-frame-options": "Prevents the page from being framed to mitigate clickjacking.",
    "content-security-policy": "Controls allowed sources for scripts/styles to mitigate XSS.",
    "strict-transport-security": "Enforces HTTPS for future requests (HSTS).",
}


def fetch(url, timeout=10):
    try:
        start = time.time()
        r = requests.get(url, timeout=timeout, allow_redirects=True)
        elapsed = time.time() - start
        return r, elapsed
    except requests.RequestException as e:
        return {"error": str(e)}, None


def check_headers(resp):
    headers = {k.lower(): v for k, v in resp.headers.items()}
    return {
        "server": headers.get("server"),
        "x_frame_options": headers.get("x-frame-options"),
        "content_security_policy": headers.get("content-security-policy"),
        "strict_transport_security": headers.get("strict-transport-security"),
        "set_cookie_header": headers.get("set-cookie"),
    }


def check_tls_cert(hostname, port=443, timeout=5):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return {
                    "subject": cert.get("subject"),
                    "issuer": cert.get("issuer"),
                    "notAfter": cert.get("notAfter"),
                }
    except Exception as e:
        return {"error": str(e)}


def parse_forms(soup):
    forms = []
    for form in soup.find_all("form"):
        inputs = [(inp.get("name"), inp.get("type")) for inp in form.find_all("input")]
        has_password = any((t and t.lower() == "password") for _, t in inputs)
        forms.append({"action": form.get("action"), "method": (form.get("method") or "get").lower(), "inputs": inputs, "has_password": has_password})
    return forms


def check_robots(base_url):
    u = urlparse(base_url)
    robots_url = f"{u.scheme}://{u.netloc}/robots.txt"
    try:
        r = requests.get(robots_url, timeout=5)
        return {"exists": r.status_code == 200, "status_code": r.status_code}
    except requests.RequestException:
        return {"exists": False}


def check_sitemap(base_url):
    u = urlparse(base_url)
    sitemap_url = f"{u.scheme}://{u.netloc}/sitemap.xml"
    try:
        r = requests.get(sitemap_url, timeout=5)
        return {"exists": r.status_code == 200, "status_code": r.status_code}
    except requests.RequestException:
        return {"exists": False}


def enumerate_links(soup, base_url):
    internal = set()
    external = set()
    parsed_base = urlparse(base_url).netloc
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(base_url, href)
        netloc = urlparse(full).netloc
        if netloc == parsed_base or netloc == "":
            internal.add(full)
        else:
            external.add(full)
    return {"internal_count": len(internal), "external_count": len(external), "internal": list(internal)[:50], "external": list(external)[:50]}


def run_all_checks(url, deep=False, timeout=10):
    result = {"url": url}

    fetched, elapsed = fetch(url, timeout=timeout)
    if isinstance(fetched, dict) and "error" in fetched:
        result["error"] = fetched["error"]
        return result

    resp = fetched
    soup = BeautifulSoup(resp.content, "html.parser")

    result["status_code"] = resp.status_code
    result["final_url"] = resp.url
    result["response_time_seconds"] = elapsed
    result["headers"] = check_headers(resp)
    result["title"] = (soup.title.string.strip() if soup.title and soup.title.string else None)
    result["meta_description"] = None
    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        result["meta_description"] = desc.get("content").strip()

    result["forms"] = parse_forms(soup)
    result["forms_count"] = len(result["forms"])

    # inline scripts
    inline_scripts = 0
    for tag in soup.find_all("script"):
        if not tag.get("src") and (tag.string and tag.string.strip()):
            inline_scripts += 1
    result["inline_scripts"] = inline_scripts

    # resources loaded over http when page is https
    parsed = urlparse(url)
    http_resources = 0
    for tag in soup.find_all(True):
        for attr in ("src", "href"):
            val = tag.get(attr)
            if val:
                full = urljoin(url, val)
                if parsed.scheme == "https" and full.startswith("http://"):
                    http_resources += 1
    result["http_resources"] = http_resources

    # cookies flags
    set_cookie = resp.headers.get("set-cookie", "")
    result["cookies_set"] = len(resp.cookies)
    result["cookies_secure_flag_present"] = "secure" in set_cookie.lower()
    result["cookies_httponly_flag_present"] = "httponly" in set_cookie.lower()

    # robots and sitemap
    result["robots"] = check_robots(url)
    result["sitemap"] = check_sitemap(url)

    # TLS certificate info if https
    if parsed.scheme == "https":
        host = parsed.hostname
        result["tls"] = check_tls_cert(host)

    if deep:
        result["links"] = enumerate_links(soup, resp.url)

    return result


def print_report(r, explain=False, json_out=None):
    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=2, ensure_ascii=False)
        print(f"Wrote JSON report to {json_out}")
        return

    if "error" in r:
        print("Error:", r["error"])
        return

    print(f"URL: {r['url']}")
    print(f"Final URL: {r.get('final_url')}")
    print(f"Status: {r.get('status_code')} (response_time: {r.get('response_time_seconds'):.2f}s)")
    headers = r.get("headers", {})
    print(f"Server header: {headers.get('server')}")
    for h in ("x_frame_options", "content_security_policy", "strict_transport_security"):
        val = headers.get(h)
        print(f"{h}: {val}")
        if explain and val is not None:
            expl = SECURITY_HEADER_EXPLANATIONS.get(h)
            if expl:
                print(f"  -> {expl}")

    print(f"Title: {r.get('title')}")
    print(f"Meta description: {r.get('meta_description')}")
    print(f"Forms: {r.get('forms_count')} (password forms: {sum(1 for f in r.get('forms', []) if f.get('has_password'))})")
    if explain and r.get('forms'):
        print("  -> Forms with password inputs should use HTTPS and proper server-side validation.")

    print(f"Inline scripts: {r.get('inline_scripts')}")
    print(f"HTTP resources on HTTPS page: {r.get('http_resources')}")
    print(f"Cookies set by server: {r.get('cookies_set')}")
    print(f"Cookies flags: Secure={r.get('cookies_secure_flag_present')}, HttpOnly={r.get('cookies_httponly_flag_present')}")
    print(f"Robots.txt: {r.get('robots')}")
    print(f"Sitemap.xml: {r.get('sitemap')}")
    if "tls" in r:
        print(f"TLS cert: {r['tls']}")

    if 'links' in r:
        l = r['links']
        print(f"Internal links: {l.get('internal_count')}, External links: {l.get('external_count')}")


def generate_html_report(r, out_path):
    title = r.get('title') or r.get('url')
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Report - {title}</title></head><body>
<h1>Report for {r.get('url')}</h1>
<ul>
  <li>Status: {r.get('status_code')}</li>
  <li>Final URL: {r.get('final_url')}</li>
  <li>Response time: {r.get('response_time_seconds')}s</li>
  <li>Title: {r.get('title')}</li>
  <li>Meta description: {r.get('meta_description')}</li>
  <li>Forms: {r.get('forms_count')}</li>
  <li>Inline scripts: {r.get('inline_scripts')}</li>
  <li>HTTP resources on HTTPS: {r.get('http_resources')}</li>
  <li>Cookies set: {r.get('cookies_set')}</li>
</ul>
<h2>Headers</h2>
<pre>{json.dumps(r.get('headers', {}), indent=2, ensure_ascii=False)}</pre>
"""
    if 'links' in r:
        links = r['links']
        html += f"<h2>Links</h2><p>Internal: {links.get('internal_count')}, External: {links.get('external_count')}</p>"
    html += "</body></html>"
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(html)


def generate_markdown_report(r, out_path):
    lines = []
    lines.append(f"# Report for {r.get('url')}")
    lines.append(f"- Status: {r.get('status_code')}")
    lines.append(f"- Final URL: {r.get('final_url')}")
    lines.append(f"- Response time: {r.get('response_time_seconds')}s")
    lines.append(f"- Title: {r.get('title')}")
    lines.append(f"- Meta description: {r.get('meta_description')}")
    lines.append(f"- Forms: {r.get('forms_count')}")
    lines.append(f"- Inline scripts: {r.get('inline_scripts')}")
    lines.append(f"- HTTP resources on HTTPS: {r.get('http_resources')}")
    lines.append(f"- Cookies set: {r.get('cookies_set')}")
    lines.append("")
    lines.append("## Headers")
    lines.append(f"```json\n{json.dumps(r.get('headers', {}), indent=2, ensure_ascii=False)}\n```")
    if 'links' in r:
        links = r['links']
        lines.append("")
        lines.append(f"## Links - Internal: {links.get('internal_count')} External: {links.get('external_count')}")
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))


def interactive_menu():
    print("safety_checker interactive menu")
    print("This menu performs passive, non-intrusive checks only.")
    while True:
        print('\nChoose an option:')
        print('1) Basic check')
        print('2) Deep check (links)')
        print('3) Check with explanations')
        print('4) JSON report to file')
        print('5) HTML report to file')
        print('6) Markdown report to file')
        print('7) Show README')
        print('0) Exit')
        choice = input('> ').strip()
        if choice == '0':
            break
        url = input('Enter URL (e.g. https://example.com): ').strip()
        if not url:
            print('No URL provided')
            continue
        if choice == '1':
            r = run_all_checks(url, deep=False)
            print_report(r)
        elif choice == '2':
            print('Deep checks enumerate links; still passive.')
            r = run_all_checks(url, deep=True)
            print_report(r)
        elif choice == '3':
            r = run_all_checks(url, deep=True)
            print_report(r, explain=True)
        elif choice == '4':
            fname = input('JSON filename to write: ').strip() or 'report.json'
            r = run_all_checks(url, deep=True)
            print_report(r, json_out=fname)
        elif choice == '5':
            fname = input('HTML filename to write: ').strip() or 'report.html'
            r = run_all_checks(url, deep=True)
            generate_html_report(r, fname)
            print(f'Wrote HTML to {fname}')
        elif choice == '6':
            fname = input('Markdown filename to write: ').strip() or 'report.md'
            r = run_all_checks(url, deep=True)
            generate_markdown_report(r, fname)
            print(f'Wrote Markdown to {fname}')
        elif choice == '7':
            try:
                with open('README.md', 'r', encoding='utf-8') as fh:
                    print('\n' + fh.read())
            except Exception as e:
                print('Could not read README.md:', e)
        else:
            print('Unknown choice')


def main():
    p = argparse.ArgumentParser(description="safety_checker: Automated webpage analysis tool")
    p.add_argument("url", nargs='?', help="URL to check")
    p.add_argument("--deep", action="store_true", help="Enumerate links and counts")
    p.add_argument("--explain", action="store_true", help="Include short explanations for findings")
    p.add_argument("--json", help="Write JSON report to file instead of printing")
    p.add_argument("--menu", action="store_true", help="Run interactive menu")
    p.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    args = p.parse_args()

    if args.menu or not args.url:
        interactive_menu()
        return

    report = run_all_checks(args.url, deep=args.deep, timeout=args.timeout)
    print_report(report, explain=args.explain, json_out=args.json)


if __name__ == "__main__":
    main()
