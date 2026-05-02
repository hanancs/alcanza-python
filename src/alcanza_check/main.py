import asyncio
import sys
import time
from rich.console import Console
from rich.table import Table
from rich import box
from alcanza_check.checks import check_dns, check_tcp, check_ssl, check_ping

async def run_checks(host: str, port: int):
    console = Console()
    
    console.print(f"\n[cyan]🔍 Checking connectivity for:[/cyan] [bold]{host}[/bold]:[bold]{port}[/bold]\n")
    
    start_time = time.time()
    
    # Run checks in parallel
    results = await asyncio.gather(
        check_ping(host),
        check_dns(host),
        check_tcp(host, port),
        check_ssl(host, port),
    )
    
    duration = int((time.time() - start_time) * 1000)
    
    table = Table(show_header=True, header_style="bold", box=box.ROUNDED)
    table.add_column("Check", width=20)
    table.add_column("Status", width=15)
    table.add_column("Details", width=40)
    
    for res in results:
        status_text = "[green]✔ PASSED[/green]" if res['status'] == 'passed' else "[red]✘ FAILED[/red]"
        table.add_row(res['name'], status_text, res['details'])
    
    console.print(table)
    console.print(f"\n[dim]Completed in {duration}ms[/dim]\n")

def main():
    args = sys.argv[1:]
    
    if len(args) < 1:
        print("Usage: alcanza-check <host> [port]")
        print("Example: alcanza-check example.com 443")
        sys.exit(1)
        
    host = args[0]
    port = int(args[1]) if len(args) > 1 else 443
    
    try:
        asyncio.run(run_checks(host, port))
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
