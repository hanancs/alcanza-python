import asyncio
import socket
import ssl
import subprocess
import time
import platform
from typing import TypedDict, Literal

class CheckResult(TypedDict):
    name: str
    status: Literal['passed', 'failed']
    details: str

async def check_dns(host: str) -> CheckResult:
    try:
        # socket.gethostbyname is blocking, run it in a thread
        loop = asyncio.get_running_loop()
        ip = await loop.run_in_executor(None, socket.gethostbyname, host)
        return {
            'name': 'DNS Lookup',
            'status': 'passed',
            'details': ip,
        }
    except Exception as e:
        return {
            'name': 'DNS Lookup',
            'status': 'failed',
            'details': str(e),
        }

async def check_tcp(host: str, port: int) -> CheckResult:
    start = time.time()
    try:
        # asyncio.open_connection is non-blocking
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=5.0
        )
        writer.close()
        await writer.wait_closed()
        duration = int((time.time() - start) * 1000)
        return {
            'name': f'TCP Port {port}',
            'status': 'passed',
            'details': f'Connected in {duration}ms',
        }
    except asyncio.TimeoutError:
        return {
            'name': f'TCP Port {port}',
            'status': 'failed',
            'details': 'Connection timed out',
        }
    except Exception as e:
        return {
            'name': f'TCP Port {port}',
            'status': 'failed',
            'details': str(e),
        }

async def check_ssl(host: str, port: int) -> CheckResult:
    try:
        context = ssl.create_default_context()
        # We want to check even if it's self-signed or invalid to get details
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        loop = asyncio.get_running_loop()
        
        def do_ssl_check():
            with socket.create_connection((host, port), timeout=5.0) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    return cert

        cert = await loop.run_in_executor(None, do_ssl_check)
        
        # In Python, getpeercert() returns a dict if verify_mode is CERT_REQUIRED
        # and validation succeeds.
        expiry = cert.get('notAfter')
        return {
            'name': 'SSL/TLS Cert',
            'status': 'passed',
            'details': f'Valid until {expiry}',
        }
    except ssl.SSLCertVerificationError as e:
        return {
            'name': 'SSL/TLS Cert',
            'status': 'failed',
            'details': f'Invalid: {e.reason}',
        }
    except Exception as e:
        return {
            'name': 'SSL/TLS Cert',
            'status': 'failed',
            'details': str(e),
        }

async def check_ping(host: str) -> CheckResult:
    is_windows = platform.system().lower() == 'windows'
    cmd = ['ping', '-n', '1', host] if is_windows else ['ping', '-c', '1', host]
    
    try:
        loop = asyncio.get_running_loop()
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            output = stdout.decode()
            details = 'Reachable'
            if is_windows:
                import re
                match = re.search(r'Average = (\d+ms)', output)
                if match:
                    details = match.group(1)
            else:
                import re
                match = re.search(r'time=(\d+\.?\d* ms)', output)
                if match:
                    details = match.group(1)
            
            return {
                'name': 'ICMP Ping',
                'status': 'passed',
                'details': details,
            }
        else:
            return {
                'name': 'ICMP Ping',
                'status': 'failed',
                'details': 'Unreachable or request timed out',
            }
    except Exception as e:
        return {
            'name': 'ICMP Ping',
            'status': 'failed',
            'details': str(e),
        }
