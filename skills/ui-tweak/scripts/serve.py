#!/usr/bin/env python3
"""Live-reload preview server for ui-tweak mocks. Standard library only.

Usage:  python3 serve.py <project>/.ui-tweak [--port 4517]

  /                      index of every tweak and its versions
  /<slug>/latest         the highest vN.html of that tweak (follows new versions)
  /<slug>/v3.html        a specific version
Every HTML page reloads itself when anything under the folder changes,
so a tab left on /<slug>/latest jumps to v(N+1) as soon as it's created.

If a server for this folder is already running (see .server), it prints that
URL and exits instead of starting a second one.
"""
import argparse, html, http.server, json, os, re, socket, socketserver, sys, urllib.request

VERSION_RE = re.compile(r"^v(\d+)\.html$")
RELOAD_JS = b"""<script>(function(){var t=null;function p(){fetch('/__changes',{cache:'no-store'}).then(function(r){return r.text()}).then(function(s){if(t!==null&&s!==t){location.reload()}t=s}).catch(function(){}).finally(function(){setTimeout(p,800)})}p()})();</script>"""


def versions(folder):
    out = []
    for name in os.listdir(folder):
        m = VERSION_RE.match(name)
        if m:
            out.append((int(m.group(1)), name))
    return sorted(out)


def fingerprint(root):
    parts = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.startswith("."):
                continue
            p = os.path.join(dirpath, f)
            try:
                parts.append(f"{p}:{os.stat(p).st_mtime_ns}")
            except OSError:
                pass
    return str(hash("|".join(sorted(parts))))


def make_handler(root):
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=root, **kw)

        def log_message(self, *a):
            pass

        def send_bytes(self, body, ctype="text/html; charset=utf-8", code=200):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def inject(self, path):
            with open(path, "rb") as fh:
                body = fh.read()
            i = body.lower().rfind(b"</body>")
            body = body[:i] + RELOAD_JS + body[i:] if i != -1 else body + RELOAD_JS
            self.send_bytes(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/__changes":
                return self.send_bytes(fingerprint(root).encode(), "text/plain")
            if path == "/__ping":
                return self.send_bytes(json.dumps({"root": root}).encode(), "application/json")
            if path in ("/", "/index.html"):
                return self.index()
            parts = [p for p in path.split("/") if p]
            if len(parts) == 2 and parts[1] == "latest":
                folder = os.path.join(root, parts[0])
                vs = versions(folder) if os.path.isdir(folder) else []
                if not vs:
                    return self.send_bytes(b"No versions yet.", "text/plain", 404)
                return self.inject(os.path.join(folder, vs[-1][1]))
            full = os.path.realpath(os.path.join(root, *parts)) if parts else root
            if full.startswith(root + os.sep) and full.endswith(".html") and os.path.isfile(full):
                return self.inject(full)
            return super().do_GET()

        def index(self):
            rows = []
            for slug in sorted(os.listdir(root)):
                folder = os.path.join(root, slug)
                if slug.startswith(".") or not os.path.isdir(folder):
                    continue
                vs = versions(folder)
                links = " · ".join(f'<a href="/{html.escape(slug)}/{n}">v{v}</a>' for v, n in reversed(vs)) or "no versions yet"
                rows.append(f'<li><a href="/{html.escape(slug)}/latest"><b>{html.escape(slug)}</b> (latest)</a><br><small>{links}</small></li>')
            body = ("<!doctype html><meta charset=utf-8><title>UI previews</title>"
                    "<style>body{font:15px/1.6 system-ui;margin:32px;max-width:720px}li{margin:0 0 14px}</style>"
                    "<h1>UI previews</h1><ul>" + ("".join(rows) or "<li>Nothing yet.</li>") + "</ul></body>")
            self.send_bytes(body.encode())

    return H


def running(state_file, root):
    try:
        with open(state_file) as fh:
            url = json.load(fh)["url"]
        with urllib.request.urlopen(url + "__ping", timeout=1) as r:
            return url if json.load(r).get("root") == root else None
    except Exception:
        return None


def free_port(start):
    for port in range(start, start + 50):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise SystemExit("No free port found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--port", type=int, default=4517)
    a = ap.parse_args()
    root = os.path.realpath(a.root)
    os.makedirs(root, exist_ok=True)
    state = os.path.join(root, ".server")
    url = running(state, root)
    if url:
        print(f"ui-tweak preview server already running: {url}", flush=True)
        return
    port = free_port(a.port)
    url = f"http://localhost:{port}/"
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", port), make_handler(root)) as srv:
        with open(state, "w") as fh:
            json.dump({"url": url, "pid": os.getpid()}, fh)
        print(f"ui-tweak preview server: {url}", flush=True)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            try:
                os.remove(state)
            except OSError:
                pass


if __name__ == "__main__":
    main()
