"""
GCP + MCP + RAG Interactive CLI Runner
Module: cli.py
Demonstrates end-to-end execution of Model Context Protocol (MCP) tool discovery,
GCP telemetry diagnosis, and 2-Stage Hybrid RAG runbook remediation.
"""

import sys
import os
import argparse
import json

# Windows UTF-8 stdout configuration
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from .agent_client import MCPSREAgent

console = Console(highlight=False)


def main():
    parser = argparse.ArgumentParser(description="GCP + MCP + RAG Enterprise SRE Assistant")
    parser.add_argument(
        "query",
        nargs="?",
        default="Investigate why payment-gateway on Cloud Run has high latency and 504 errors.",
        help="SRE troubleshooting query"
    )
    args = parser.parse_args()

    # 1. Header Banner
    console.print(Panel(
        "[bold cyan]🌐 GCP + MCP + RAG ENTERPRISE SRE AGENT[/bold cyan]\n"
        "[white]Infrastructure:[/] Google Cloud Run & Cloud SQL  |  "
        "[white]Protocol:[/] Model Context Protocol (MCP 2024-11-05)  |  "
        "[white]RAG:[/] 2-Stage Hybrid RRF (k=60)",
        border_style="cyan"
    ))

    # 2. Initialize Agent & Discover Tools via MCP
    agent = MCPSREAgent()

    table_tools = Table(title="Discovered Tools via MCP (tools/list)", show_lines=True)
    table_tools.add_column("Tool Name", style="bold green", width=26)
    table_tools.add_column("Description", style="white")

    for t in agent.discovered_tools:
        table_tools.add_row(t.get("name"), t.get("description"))
    console.print(table_tools)

    console.print(f"\n[bold yellow]User Query:[/] \"{args.query}\"\n")

    # 3. Execute MCP Diagnostic & Remediation Flow
    with console.status("[bold cyan]Executing MCP Diagnostic & RAG Pipeline...[/bold cyan]"):
        report = agent.diagnose_and_remediate(args.query, auto_remediate=True)

    # 4. Display Workflow Execution Logs
    console.print("[bold cyan]━━━ MCP Execution Trace & Tool Invocations ━━━[/bold cyan]")
    for step in report["steps_log"]:
        console.print(f"[dim white]• {step}[/dim white]")

    # 5. Telemetry & RAG Runbook Inspection Cards
    console.print("")
    initial_svc = report["initial_telemetry"]
    runbook = report["grounded_runbook"]

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column()
    grid.add_column()

    card_telemetry = Panel(
        f"[bold]Service:[/] {initial_svc.get('service_name')}\n"
        f"[bold]Initial Status:[/] [bold red]{initial_svc.get('status')}[/bold red]\n"
        f"[bold]P99 Latency:[/] [red]{initial_svc.get('p99_latency_ms')} ms[/red]\n"
        f"[bold]504 Error Rate:[/] [red]{initial_svc.get('error_rate_504')}[/red]\n"
        f"[bold]Min Instances:[/] {initial_svc.get('min_instances')} (Cold starts enabled)\n"
        f"[bold]Concurrency:[/] {initial_svc.get('container_concurrency')}",
        title="[bold red]1. Live GCP Cloud Run Telemetry[/bold red]",
        border_style="red"
    )

    card_rag = Panel(
        f"[bold]Runbook ID:[/] [cyan]{runbook.get('doc_id')}[/cyan]\n"
        f"[bold]Section:[/] {runbook.get('title')}\n"
        f"[bold]RRF Score:[/] [yellow]{runbook.get('rrf_score', 0):.5f}[/yellow]\n"
        f"[dim]{runbook.get('text', '')[:220]}...[/dim]",
        title="[bold green]2. Grounded Enterprise RAG Knowledge[/bold green]",
        border_style="green"
    )

    grid.add_row(card_telemetry, card_rag)
    console.print(grid)

    # 6. Remediation Result
    if report.get("remediation_result"):
        rem = report["remediation_result"]
        upd = rem.get("updated_state", {})
        console.print(Panel(
            f"[bold green]✔ Remediation Action Executed Successfully via MCP 'update_cloud_run_scaling'![/bold green]\n\n"
            f"[white]• New Status:[/] [bold green]{upd.get('status')}[/bold green]\n"
            f"[white]• Min Instances:[/] {upd.get('min_instances')} (Warm pool active)\n"
            f"[white]• Max Instances:[/] {upd.get('max_instances')}\n"
            f"[white]• Concurrency Budget:[/] {upd.get('container_concurrency')}\n"
            f"[white]• CPU Boost:[/] {upd.get('cpu_boost_enabled')}\n"
            f"[white]• Post-Remediation P99 Latency:[/] [bold green]{upd.get('p99_latency_ms')} ms[/bold green] (Down from {initial_svc.get('p99_latency_ms')} ms)",
            title="[bold green]3. Audited GCP Infrastructure Remediation (MCP Output)[/bold green]",
            border_style="green"
        ))


if __name__ == "__main__":
    main()
