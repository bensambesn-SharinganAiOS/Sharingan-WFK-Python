#!/usr/bin/env python3
"""
Persistent Browser Server - Run browser independently
Usage: python3 browser_daemon.py
The browser will stay open even when this script ends.
Access: VNC on port 5900 or connect via socket port 9999
"""
import os
import sys
import time
import socket
import signal
import atexit
from threading import Thread

from sharingan_app._internal.browser_controller_complete import BrowserController

PID_FILE = "/tmp/browser_daemon.pid"
LOG_FILE = "/tmp/browser_daemon.log"

class BrowserDaemon:
    def __init__(self):
        self.ctrl = None
        self.running = True
        self.pid = os.getpid()
        
    def log(self, msg):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{ts}] {msg}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_msg)
        print(log_msg.strip())
        
    def cleanup(self):
        self.log("Cleaning up...")
        if self.ctrl and self.ctrl.driver:
            self.log("Browser still running - keeping it open for user")
        self.log("Daemon exiting but browser may still be running")
        
    def start_browser(self):
        self.log("Starting persistent browser...")
        self.ctrl = BrowserController('chrome', headless=False)
        result = self.ctrl.launch_browser()
        self.log(f"Browser launch: {result}")
        
        if result.get('status') == 'success':
            self.ctrl.navigate("https://github.com/login")
            time.sleep(2)
            self.log(f"Navigated to: {self.ctrl.current_url}")
            self.log("Browser is now OPEN and INDEPENDENT")
            self.log("You can interact with it directly via the GUI")
            self.log("Browser will NOT close when this script exits")
        return result
    
    def start_socket_server(self):
        """Socket server for remote control"""
        host = 'localhost'
        port = 9999
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        self.log(f"Socket server listening on {host}:{port}")
        
        while self.running:
            try:
                server.settimeout(1.0)
                try:
                    conn, addr = server.accept()
                except socket.timeout:
                    continue
                    
                self.log(f"Connection from {addr}")
                try:
                    data = conn.recv(1024).decode().strip()
                    self.log(f"Command: {data}")
                    
                    parts = data.split(' ', 1)
                    cmd = parts[0].upper()
                    arg = parts[1] if len(parts) > 1 else ""
                    
                    if cmd == 'URL':
                        conn.send(f"{self.ctrl.current_url}\n".encode())
                    elif cmd == 'TITLE':
                        conn.send(f"{self.ctrl.driver.title}\n".encode())
                    elif cmd == 'NAVIGATE':
                        self.ctrl.navigate(arg)
                        conn.send(b"OK\n")
                    elif cmd == 'CLICK':
                        res = self.ctrl.click(arg)
                        conn.send(f"{res}\n".encode())
                    elif cmd == 'HTML':
                        html = self.ctrl.get_page_source().get('html', '')[:3000]
                        conn.send(html.encode())
                    elif cmd == 'SCREENSHOT':
                        self.ctrl.take_screenshot("/tmp/browser_screenshot.png")
                        conn.send(b"OK\n")
                    elif cmd == 'QUIT':
                        conn.send(b"BYE\n")
                        self.running = False
                    else:
                        conn.send(f"Unknown: {cmd}\n".encode())
                except Exception as e:
                    self.log(f"Error: {e}")
                finally:
                    conn.close()
            except Exception as e:
                self.log(f"Server error: {e}")
                
    def run(self):
        atexit.register(self.cleanup)
        
        # Write PID file
        with open(PID_FILE, "w") as f:
            f.write(str(self.pid))
        self.log(f"Daemon started with PID: {self.pid}")
        
        # Start browser
        self.start_browser()
        
        # Start socket server in background
        server_thread = Thread(target=self.start_socket_server, daemon=True)
        server_thread.start()
        
        self.log("Browser is INDEPENDENT and OPEN")
        self.log("Commands: URL, TITLE, NAVIGATE <url>, CLICK <selector>, HTML, QUIT")
        self.log("Connect: nc localhost 9999")
        self.log("VNC: Connect to localhost:5900 (if x11vnc running)")
        
        # Keep alive
        try:
            while self.running:
                time.sleep(5)
                if self.ctrl and self.ctrl.driver:
                    pass  # Browser is alive
        except KeyboardInterrupt:
            self.log("Interrupted")
            self.running = False

if __name__ == "__main__":
    daemon = BrowserDaemon()
    daemon.run()
