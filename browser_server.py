#!/usr/bin/env python3
"""
Persistent browser server - maintains browser session across calls
Usage: python3 browser_server.py [port]
Then connect with: nc localhost 9999
Commands:
  GET_URL - get current URL
  NAVIGATE <url> - go to URL
  CLICK <selector> - click element
  FIND <selector> - find element
  QUIT - close browser and exit
"""
import socket
import sys
import time

from sharingan_app._internal.browser_controller_complete import BrowserController

HOST = 'localhost'
PORT = 9999

class BrowserServer:
    def __init__(self):
        self.ctrl = BrowserController('chrome', headless=False)
        self.running = True
        
    def start(self):
        print("Starting browser...")
        self.ctrl.launch_browser()
        print(f"Browser started. Go to http://localhost:9222 to inspect" if False else "")
        
    def handle_client(self, conn, addr):
        print(f"Client connected from {addr}")
        try:
            while self.running:
                data = conn.recv(4096).decode('utf-8').strip()
                if not data:
                    continue
                    
                print(f"Command: {data}")
                parts = data.split(' ', 1)
                cmd = parts[0].upper()
                
                if cmd == 'GET_URL':
                    conn.send(f"URL: {self.ctrl.current_url}\n".encode())
                    
                elif cmd == 'TITLE':
                    title = self.ctrl.driver.title if self.ctrl.driver else "N/A"
                    conn.send(f"{title}\n".encode())
                    
                elif cmd == 'NAVIGATE':
                    url = parts[1] if len(parts) > 1 else "https://google.com"
                    self.ctrl.navigate(url)
                    conn.send(f"OK\n".encode())
                    
                elif cmd == 'CLICK':
                    selector = parts[1] if len(parts) > 1 else ""
                    if selector:
                        result = self.ctrl.click(selector)
                        conn.send(f"{result}\n".encode())
                    else:
                        conn.send("ERROR: missing selector\n".encode())
                        
                elif cmd == 'FIND':
                    selector = parts[1] if len(parts) > 1 else ""
                    if selector:
                        result = self.ctrl.find_elements(selector)
                        conn.send(f"{result}\n".encode())
                    else:
                        conn.send("ERROR: missing selector\n".encode())
                        
                elif cmd == 'HTML':
                    result = self.ctrl.get_page_source()
                    conn.send(result.get('html', '')[:2000].encode())
                    
                elif cmd == 'QUIT':
                    self.ctrl.close_browser()
                    self.running = False
                    conn.send(b"BYE")
                    break
                    
                else:
                    conn.send(f"Unknown command: {cmd}\n".encode())
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
            print("Client disconnected")

def main():
    server = BrowserServer()
    server.start()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on {HOST}:{PORT}")
        print("Commands: GET_URL, NAVIGATE <url>, CLICK <selector>, FIND <selector>, HTML, QUIT")
        
        while True:
            conn, addr = s.accept()
            server.handle_client(conn, addr)
            if not server.running:
                break

if __name__ == "__main__":
    main()
