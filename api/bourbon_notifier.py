from http.server import BaseHTTPRequestHandler
from datetime import datetime

from ohlq import main as bourbon_notifier

class handler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    result = bourbon_notifier()
    print(result)
    # self.wfile.write(str(result).encode())
    return