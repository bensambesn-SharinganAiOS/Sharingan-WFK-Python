"""
strace Wrapper for Sharingan OS
Real system call tracer
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.strace")

class StraceResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 syscalls_count: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.syscalls_count = syscalls_count
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'strace'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['strace', '--version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"

def trace_program(program: str, args: str = "", count: int = None,
                 output_file: str = None) -> StraceResult:
    cmd = ['strace']
    
    if count:
        cmd.extend(['-c', '-q'])
    else:
        cmd.extend(['-f'])
    
    if output_file:
        cmd.extend(['-o', output_file])
    
    if args:
        cmd.extend(args.split())
    
    cmd.append(program)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        syscalls = output.count(' ')
        return StraceResult(success=True, command=' '.join(cmd),
                          output=output[:3000], syscalls_count=syscalls)
    except subprocess.TimeoutExpired:
        return StraceResult(success=False, command=' '.join(cmd),
                           error="Trace timeout expired")
    except Exception as e:
        return StraceResult(success=False, command=' '.join(cmd), error=str(e))

def trace_pid(pid: int, count: int = 100) -> StraceResult:
    cmd = ['strace', '-c', '-q', '-p', str(pid)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return StraceResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return StraceResult(success=False, command=' '.join(cmd), error=str(e))

def trace_file_operations(program: str, args: str = "") -> StraceResult:
    cmd = ['strace', '-e', 'trace=file', '-f']
    
    if args:
        cmd.extend(args.split())
    
    cmd.append(program)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return StraceResult(success=True, command=' '.join(cmd),
                          output=output[:3000], syscalls_count=output.count('open'))
    except Exception as e:
        return StraceResult(success=False, command=' '.join(cmd), error=str(e))

def trace_network_operations(program: str, args: str = "") -> StraceResult:
    cmd = ['strace', '-e', 'trace=network', '-f']
    
    if args:
        cmd.extend(args.split())
    
    cmd.append(program)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return StraceResult(success=True, command=' '.join(cmd),
                          output=output[:3000])
    except Exception as e:
        return StraceResult(success=False, command=' '.join(cmd), error=str(e))

def get_help() -> str:
    try:
        result = subprocess.run(['strace', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'trace' in query_lower and ('program' in query_lower or 'executable' in query_lower or 'binary' in query_lower):
        program_match = re.search(r'(?:programme|program|binary|executable)\s*:?\s*(\S+)', query)
        if program_match:
            program = program_match.group(1)
            args_match = re.search(r'(?:args|arguments)\s*:?\s*(.+)', query)
            args = args_match.group(1) if args_match else ""
            result = trace_program(program, args)
            return {'action': 'trace', 'success': result.success,
                   'program': program, 'syscalls': result.syscalls_count,
                   'output': result.output[:500]}
        
        program_match = re.search(r'(\S+\.(?:bin|exe|elf|sh))', query)
        if program_match:
            program = program_match.group(1)
            result = trace_program(program)
            return {'action': 'trace', 'success': result.success,
                   'program': program, 'output': result.output[:500]}
        
        return {'action': 'trace', 'success': False,
               'error': 'Program required',
               'example': 'trace program /bin/ls'}
    
    if 'trace' in query_lower and 'pid' in query_lower:
        pid_match = re.search(r'pid\s*:?\s*(\d+)', query)
        if pid_match:
            pid = int(pid_match.group(1))
            result = trace_pid(pid)
            return {'action': 'trace_pid', 'success': result.success,
                   'pid': pid, 'output': result.output[:500]}
        
        return {'action': 'trace_pid', 'success': False,
               'error': 'PID required', 'example': 'trace pid 1234'}
    
    if 'file' in query_lower and 'trace' in query_lower:
        program_match = re.search(r'(\S+\.(?:bin|exe|elf|sh))', query)
        if program_match:
            program = program_match.group(1)
            result = trace_file_operations(program)
            return {'action': 'trace_file', 'success': result.success,
                   'program': program, 'output': result.output[:500]}
        
        return {'action': 'trace_file', 'success': False,
               'error': 'Program required'}
    
    if 'network' in query_lower and 'trace' in query_lower:
        program_match = re.search(r'(\S+\.(?:bin|exe|elf|sh))', query)
        if program_match:
            program = program_match.group(1)
            result = trace_network_operations(program)
            return {'action': 'trace_network', 'success': result.success,
                   'program': program, 'output': result.output[:500]}
        
        return {'action': 'trace_network', 'success': False,
               'error': 'Program required'}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'note': 'System call tracer for program analysis'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'trace program /bin/ls'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'strace',
        'description': 'System call tracer',
        'category': 'forensics',
        'supported_queries': [
            'quelle est la version de strace',
            'trace program /bin/ls',
            'trace pid 1234',
            'trace file operations of /bin/ls',
            'trace network operations of /bin/ls',
            'strace help',
            'informations sur strace'
        ],
        'warning': 'Use for legitimate debugging and analysis only.',
        'features': ['trace program', 'trace pid', 'trace file ops', 'trace network ops']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("strace Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'trace':
        if len(sys.argv) > 2:
            result = trace_program(sys.argv[2])
            print(f"Program: {sys.argv[2]}")
            print(f"Syscalls: {result.syscalls_count}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
