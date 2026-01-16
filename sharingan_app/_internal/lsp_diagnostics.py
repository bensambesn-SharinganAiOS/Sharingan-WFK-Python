#!/usr/bin/env python3
"""
LSP Diagnostics Integration - Real-time code feedback
Inspired by OpenCode's LSP integration
"""

import subprocess
import json
import time
import os
import shutil
import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.lsp")

@dataclass
class Diagnostic:
    file_path: str
    line: int
    column: int
    severity: str  # error, warning, info, hint
    code: str
    message: str
    source: str

class LSPServer:
    """Language Server Protocol client for diagnostics"""
    
    LANGUAGE_SERVERS = {
        "python": ["pyright-langserver", "pylsp"],
        "javascript": ["typescript-language-server", "javascript-typescript-stdio"],
        "typescript": ["typescript-language-server", "tsserver"],
        "go": ["gopls"],
        "rust": ["rust-analyzer"],
        "java": ["jdtls"],
        "cpp": ["clangd"],
    }
    
    def __init__(self, language: str = "python"):
        self.language = language
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.responses: Dict[int, Dict] = {}
        self.lock = threading.Lock()
        self.diagnostics: Dict[str, List[Diagnostic]] = {}
        self._start_server()
    
    def _get_server_command(self) -> List[str]:
        """Get command to start LSP server"""
        servers = self.LANGUAGE_SERVERS.get(self.language, [])
        
        for server in servers:
            path = shutil.which(server)
            if path:
                return [path, "--stdio"]
        
        return []
    
    def _start_server(self):
        """Start LSP server process"""
        cmd = self._get_server_command()
        if not cmd:
            logger.warning(f"No LSP server found for {self.language}")
            return
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent.parent
            )
            logger.info(f"LSP server started for {self.language}")
        except Exception as e:
            logger.error(f"Failed to start LSP server: {e}")
    
    def _send_request(self, method: str, params: Dict) -> int:
        """Send request to LSP server"""
        if not self.process or not self.process.stdin:
            return -1
        
        self.request_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        content = json.dumps(message)
        try:
            self.process.stdin.write(f"Content-Length: {len(content)}\r\n\r\n{content}".encode())
            self.process.stdin.flush()
        except:
            pass
        
        return self.request_id
    
    def _read_response(self, timeout: float = 5.0) -> Optional[Dict]:
        """Read response from LSP server"""
        if not self.process or not self.process.stdout:
            return None
        
        import select
        
        start = time.time()
        while time.time() - start < timeout:
            if select.select([self.process.stdout], [], [], 0.1)[0]:
                header = b""
                while b"\r\n\r\n" not in header:
                    header += self.process.stdout.read(1)
                
                content_length = 0
                for line in header.decode().split("\r\n"):
                    if line.startswith("Content-Length:"):
                        content_length = int(line.split(":")[1].strip())
                        break
                
                content = self.process.stdout.read(content_length)
                return json.loads(content.decode())
        
        return None
    
    def initialize(self, root_path: str):
        """Initialize LSP session"""
        if not self.process:
            return
        
        params = {
            "processId": os.getpid(),
            "rootPath": root_path,
            "rootUri": f"file://{root_path}",
            "capabilities": {},
            "workspaceFolders": [{"uri": f"file://{root_path}", "name": "project"}]
        }
        
        self._send_request("initialize", params)
        self._read_response()
        
        self._send_request("initialized", {})
    
    def open_file(self, file_path: str, content: str):
        """Notify server that file is open"""
        if not self.process:
            return
        
        params = {
            "textDocument": {
                "uri": f"file://{file_path}",
                "languageId": self.language,
                "version": 1,
                "text": content
            }
        }
        self._send_request("textDocument/didOpen", params)
    
    def update_file(self, file_path: str, content: str, version: int = 1):
        """Notify server of file changes"""
        if not self.process:
            return
        
        params = {
            "textDocument": {
                "uri": f"file://{file_path}",
                "version": version
            },
            "contentChanges": [{"text": content}]
        }
        self._send_request("textDocument/didChange", params)
    
    def get_diagnostics(self, file_path: str) -> List[Diagnostic]:
        """Get diagnostics for a file"""
        return self.diagnostics.get(file_path, [])
    
    def _handle_diagnostic_notification(self, params: Dict):
        """Handle diagnostic notification from server"""
        for diag in params.get("diagnostics", []):
            range_data = diag.get("range", {})
            start = range_data.get("start", {})
            
            diagnostic = Diagnostic(
                file_path=params.get("uri", "").replace("file://", ""),
                line=start.get("line", 0),
                column=start.get("character", 0),
                severity=diag.get("severity", "error"),
                code=diag.get("code", ""),
                message=diag.get("message", ""),
                source=diag.get("source", "")
            )
            
            if diagnostic.file_path not in self.diagnostics:
                self.diagnostics[diagnostic.file_path] = []
            self.diagnostics[diagnostic.file_path].append(diagnostic)
    
    def check_file(self, file_path: str) -> List[Diagnostic]:
        """Check file for diagnostics and return issues"""
        if not Path(file_path).exists():
            return []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            self.open_file(file_path, content)
            time.sleep(0.5)
            
            return self.diagnostics.get(file_path, [])
        except Exception as e:
            logger.error(f"Failed to check file: {e}")
            return []
    
    def validate_code(self, file_path: str, code: str) -> List[Dict]:
        """Validate code and return issues in structured format"""
        issues = []
        
        if not Path(file_path).exists():
            return [{"type": "error", "message": "File does not exist"}]
        
        try:
            with open(file_path, 'w') as f:
                f.write(code)
            
            diagnostics = self.check_file(file_path)
            
            for diag in diagnostics:
                issues.append({
                    "type": diag.severity,
                    "file": diag.file_path,
                    "line": diag.line + 1,
                    "column": diag.column + 1,
                    "code": diag.code,
                    "message": diag.message,
                    "source": diag.source
                })
            
            return issues
        except Exception as e:
            return [{"type": "error", "message": str(e)}]
    
    def close(self):
        """Close LSP session"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None


class SimpleDiagnostics:
    """Simple diagnostics without full LSP (fallback)"""
    
    @staticmethod
    def check_python_syntax(code: str) -> List[Dict]:
        """Check Python syntax without running"""
        import ast
        
        issues = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                "type": "error",
                "line": e.lineno or 1,
                "column": e.offset or 1,
                "message": str(e.msg),
                "code": "syntax-error"
            })
        except Exception as e:
            issues.append({
                "type": "error",
                "message": str(e)
            })
        
        return issues
    
    @staticmethod
    def check_common_issues(code: str) -> List[Dict]:
        """Check for common code issues"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if '\t' in line and '    ' not in line:
                if i > 1:
                    issues.append({
                        "type": "warning",
                        "line": i,
                        "message": "Mixed tabs and spaces detected",
                        "code": "indent-mixed"
                    })
            
            if len(line) > 120:
                issues.append({
                    "type": "warning",
                    "line": i,
                    "message": f"Line exceeds 120 characters ({len(line)} chars)",
                    "code": "line-too-long"
                })
        
        return issues
    
    @staticmethod
    def validate_code(file_path: str, code: str) -> List[Dict]:
        """Validate code and return issues"""
        issues = []
        
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            issues.extend(SimpleDiagnostics.check_python_syntax(code))
            issues.extend(SimpleDiagnostics.check_common_issues(code))
        elif ext in ['.js', '.ts']:
            issues.extend(SimpleDiagnostics.check_common_issues(code))
        else:
            issues.extend(SimpleDiagnostics.check_common_issues(code))
        
        return issues


class DiagnosticManager:
    """Manages diagnostics for the coding agent"""
    
    def __init__(self):
        self.lsp_servers: Dict[str, LSPServer] = {}
        self.simple_checker = SimpleDiagnostics()
    
    def get_server(self, language: str) -> LSPServer:
        """Get or create LSP server for language"""
        if language not in self.lsp_servers:
            self.lsp_servers[language] = LSPServer(language)
        return self.lsp_servers[language]
    
    def validate_file(self, file_path: str) -> List[Dict]:
        """Validate a file and return diagnostics"""
        if not Path(file_path).exists():
            return [{"type": "error", "message": "File not found"}]
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            ext = Path(file_path).suffix.lower().strip('.')
            
            try:
                server = self.get_server(ext)
                return server.validate_code(file_path, code)
            except Exception as e:
                return self.simple_checker.validate_code(file_path, code)
        except Exception as e:
            return [{"type": "error", "message": str(e)}]
    
    def validate_code(self, file_path: str, code: str) -> List[Dict]:
        """Validate code directly (before saving)"""
        ext = Path(file_path).suffix.lower().strip('.')
        
        try:
            server = self.get_server(ext)
            return server.validate_code(file_path, code)
        except Exception as e:
            return self.simple_checker.validate_code(file_path, code)
    
    def check_after_edit(self, file_path: str, old_code: str, new_code: str) -> List[Dict]:
        """Check for issues after editing a file"""
        return self.validate_file(file_path)
    
    def format_diagnostics(self, issues: List[Dict]) -> str:
        """Format diagnostics for display"""
        if not issues:
            return "✓ No issues detected"
        
        output = []
        error_count = sum(1 for i in issues if i.get("type") == "error")
        warning_count = sum(1 for i in issues if i.get("type") == "warning")
        
        output.append(f"Issues: {len(issues)} ({error_count} errors, {warning_count} warnings)")
        
        for issue in issues:
            line = issue.get("line", "?")
            msg = issue.get("message", "Unknown issue")
            code = issue.get("code", "")
            icon = "✗" if issue.get("type") == "error" else "!"
            
            if code:
                output.append(f"  {icon} [{code}] Line {line}: {msg}")
            else:
                output.append(f"  {icon} Line {line}: {msg}")
        
        return "\n".join(output)


def get_diagnostic_manager() -> DiagnosticManager:
    """Get diagnostic manager singleton"""
    return DiagnosticManager()


if __name__ == "__main__":
    print("=== DIAGNOSTICS SYSTEM TEST ===\n")
    
    manager = get_diagnostic_manager()
    
    print("1. Simple syntax check:")
    code = """
def test():
    if True:
        print("hello"
    return 0
"""
    issues = SimpleDiagnostics.check_python_syntax(code)
    print(f"   Found {len(issues)} issues")
    for issue in issues:
        print(f"   - Line {issue['line']}: {issue['message']}")
    
    print("\n2. Common issues check:")
    code2 = "x = 1\t# mixed tabs and spaces on a very long line that exceeds one hundred and twenty characters for testing purposes"
    issues2 = SimpleDiagnostics.check_common_issues(code2)
    print(f"   Found {len(issues2)} issues")
    
    print("\n3. Full validation:")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def hello():\n    print('hello')\n")
        temp_path = f.name
    
    issues3 = manager.validate_file(temp_path)
    print(f"   File: {temp_path}")
    print(f"   Issues: {len(issues3)}")
    print(manager.format_diagnostics(issues3))
    
    os.unlink(temp_path)
    
    print("\n✓ Diagnostics system ready!")
