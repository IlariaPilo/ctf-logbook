from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse

url = ''
port = 0
address = ''

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', url)
        self.end_headers()

if __name__ == "__main__":
    # read parameters
    parser = argparse.ArgumentParser(description="A simple Python server redirecting requests.")

    parser.add_argument('-p', '--port', type=int, default=8000, help='Server port number [default: 8000]')
    parser.add_argument('-a', '--address', type=str, default='localhost', help='Server address [default: localhost]')
    parser.add_argument('url', type=str, help='URL requests are redirected to')

    args = parser.parse_args()

    # Display the arguments
    url = args.url
    port = args.port
    address = args.address

    server_address = (address, port)
    httpd = HTTPServer(server_address, RedirectHandler)
    print(f'Redirecting server running on port {port}...')
    httpd.serve_forever()

