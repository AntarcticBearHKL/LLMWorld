import http.server
import socketserver
import os
import webbrowser
import threading
import json
from urllib.parse import urlparse, parse_qs

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/dates':
            self.handle_get_dates(parsed_path.query)
        else:
            # 使用默认文件服务器
            super().do_GET()
    
    def handle_get_dates(self, query_string):
        try:
            params = parse_qs(query_string)
            world_id = params.get('world_id', ['109'])[0]
            postcode = params.get('postcode', ['3168'])[0]
            house_id = params.get('house_id', ['house_0001'])[0]
            
            outputs_path = f'outputs/{world_id}/{postcode}/{house_id}'
            
            if not os.path.exists(outputs_path):
                self.send_json_response([])
                return
            
            dates = []
            for item in os.listdir(outputs_path):
                item_path = os.path.join(outputs_path, item)
                if os.path.isdir(item_path) and item.isdigit() and len(item) == 8:
                    # 检查是否有必要的JSON文件
                    test_file = os.path.join(item_path, '04_第四层_批量用电决策_David Chen.json')
                    if os.path.exists(test_file):
                        dates.append(item)
            
            dates.sort()
            self.send_json_response(dates)
            
        except Exception as e:
            print(f"Error getting dates: {e}")
            self.send_json_response([])
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()

def open_browser():
    webbrowser.open(f'http://localhost:{PORT}/render/')

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}/render/")
    print(f"Press Ctrl+C to stop the server")
    
    threading.Timer(1.5, open_browser).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
