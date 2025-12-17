import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class MockTSAHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # respond with a simple fixed token (binary)
        self.send_response(200)
        self.send_header("Content-Type", "application/timestamp-reply")
        self.end_headers()
        self.wfile.write(b"\x30\x31\x32\x33")

    def log_message(self, format, *args):
        return


def run_server(port):
    srv = HTTPServer(("127.0.0.1", port), MockTSAHandler)
    srv.serve_forever()


def test_rfc3161_integration(tmp_path):
    port = 35000
    t = threading.Thread(target=run_server, args=(port,), daemon=True)
    t.start()
    tsa_url = f"http://127.0.0.1:{port}/"
    os.environ["TIMESTAMP_PROVIDER"] = "rfc3161"
    os.environ["TSA_URL"] = tsa_url
    from sealledger.timestamp import get_provider

    p = get_provider()
    res = p.anchor(b"payload")
    assert res.get("method") == "rfc3161"
    assert res.get("tsa_url") == tsa_url
    assert "anchor_token" in res
