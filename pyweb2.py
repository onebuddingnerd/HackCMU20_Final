from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib

HOST_ADDRESS = ""
HOST_PORT = 8080

class RequestHandler(BaseHTTPRequestHandler):
    """ Our custom, example request handler """
    
    def send_response(self, code, message=None):
        """ override to customize header """
        self.log_request(code)
        self.send_response_only(code)
        self.send_header('Server','python3 http.server Development Server')     
        self.send_header('Date', self.date_time_string())
        self.end_headers()  
    
    def do_GET(self):
        """ response for a GET request """
        self.send_response(200)
        self.wfile.write(b'<head><style>p, button {font-size: 1em}</style></head>')
        self.wfile.write(b'<body>')
        self.wfile.write(b'<form method="POST" enctype="application/x-www-form-urlencoded">')
        self.wfile.write(b'<span>Enter something:</span>\
                            <input name="test"> \
                            <button style="color:blue">Submit</button>')
        self.wfile.write(b'</form>')    
        self.wfile.write(b'</body>')
        
    def do_POST(self):
        """ response for a POST """
        content_length = int(self.headers['Content-Length'])
        (input,value) = self.rfile.read(content_length).decode('utf-8').split('=')
        value = urllib.parse.unquote_plus(value)
        self.send_response(200)
        self.wfile.write(b'<head><style>p, button {font-size: 1em}</style></head>')
        self.wfile.write(b'<body>')
        self.wfile.write(b'<p>You submitted ' + bytes(value,'utf-8') + b'</p>')
        self.wfile.write(b'</body>')    
  
def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    """ follows example shown on docs.python.org """
    server_address = (HOST_ADDRESS, HOST_PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run(handler_class=RequestHandler)