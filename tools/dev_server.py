"""Static file server for the asset preview + a POST endpoint that saves rendered PNGs.
Usage: python3 tools/dev_server.py  (serves the project root on :8765)
POST /save?name=<file>.png  body = dataURL  ->  public/assets/ui/renders/<file>.png"""
import base64, http.server, os, re, urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEST = os.path.join(ROOT, 'public', 'assets', 'ui', 'renders')


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()

    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = q.get('name', [''])[0]
        if not re.fullmatch(r'[a-z0-9_]+\.(png|jpg)', name):
            self.send_error(400, 'bad name'); return
        body = self.rfile.read(int(self.headers['Content-Length'])).decode()
        data = base64.b64decode(body.split(',', 1)[1])
        os.makedirs(DEST, exist_ok=True)
        with open(os.path.join(DEST, name), 'wb') as f: f.write(data)
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok')


if __name__ == '__main__':
    http.server.ThreadingHTTPServer(('127.0.0.1', 8765), H).serve_forever()
