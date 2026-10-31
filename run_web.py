import http.server
import socket
import socketserver
import webbrowser
from pathlib import Path
import os

PORT = 8080

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass
    try:
        import subprocess
        out = subprocess.check_output(["ifconfig"]).decode()
        for line in out.splitlines():
            if "inet " in line and "127.0.0.1" not in line:
                return line.split()[1]
    except Exception:
        pass
    return "172.20.10.2"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

def main():
    # Ensure working directory is project root
    os.chdir(Path(__file__).parent)
    local_ip = get_local_ip()

    print("=" * 62)
    print("🎬 ASCII Mystery Cinema Web App is LIVE!")
    print(f"📱 Local URL (this Mac):     http://localhost:{PORT}")
    print(f"📱 Phone URL (Android/iOS):  http://{local_ip}:{PORT}")
    print("   (Phone and Mac must be connected to the same Wi-Fi)")
    print("=" * 62)
    print("Opening browser...")

    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass

    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    main()
