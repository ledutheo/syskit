"""Main CLI application for syskit."""

from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from syskit import __version__

app = typer.Typer(
    name="syskit",
    help="Modern CLI toolkit for Arch Linux and Manjaro users",
    add_completion=True,
    rich_markup_mode="rich",
)
console = Console()


def run_command(cmd: list[str], capture: bool = True) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip() if e.stderr else str(e)}"
    except FileNotFoundError:
        return f"Command not found: {cmd[0]}"


def command_failed(output: str) -> bool:
    """Return True when run_command reported a failure."""
    if not isinstance(output, str):
        return False
    return output.startswith("Error:") or output.startswith("Command not found:")


@app.command()
def info() -> None:
    """Display detailed system information."""
    console.print(Panel.fit("🖥️  System Information", style="bold blue"))

    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")

    # Basic info
    table.add_row("Hostname", platform.node())
    table.add_row("Kernel", platform.release())
    table.add_row("Architecture", platform.machine())
    table.add_row("Python", platform.python_version())

    # Distro info
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    distro = line.split("=")[1].strip().strip('"')
                    table.add_row("Distribution", distro)
                    break
    except FileNotFoundError:
        pass

    # Uptime
    uptime = run_command(["uptime", "-p"])
    table.add_row("Uptime", uptime)

    # Memory
    mem = run_command(["free", "-h"])
    if "Error" not in mem:
        lines = mem.split("\n")
        if len(lines) > 1:
            mem_info = lines[1].split()
            if len(mem_info) >= 3:
                table.add_row("Memory", f"{mem_info[2]} / {mem_info[1]}")

    console.print(table)


@app.command()
def clean(
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be cleaned"),
) -> None:
    """Clean system caches, logs and orphan packages."""
    console.print(Panel.fit("🧹 System Cleanup", style="bold yellow"))

    actions = []

    # Orphan packages
    orphans = run_command(["pacman", "-Qtdq"])
    if orphans and "Error" not in orphans:
        pkgs = orphans.split()
        actions.append(f"Remove {len(pkgs)} orphan packages: {', '.join(pkgs[:5])}...")

    # Pacman cache
    actions.append("Clean pacman package cache")

    # Journal logs older than 2 weeks
    actions.append("Vacuum journal logs older than 2 weeks")

    # User cache (thumbnails, etc.)
    cache_dir = Path.home() / ".cache"
    if cache_dir.exists():
        actions.append("Clean user cache (thumbnails, etc.)")

    for action in actions:
        console.print(f"  [yellow]→[/yellow] {action}")

    if dry_run:
        console.print("\n[bold yellow]Dry run mode - nothing was actually cleaned.[/bold yellow]")
        return

    if typer.confirm("\nProceed with cleanup?"):
        console.print("\n[green]Running cleanup...[/green]")
        warnings: list[str] = []

        if orphans and not command_failed(orphans):
            pkgs = orphans.split()
            if pkgs:
                result = run_command(["sudo", "pacman", "-Rns", "--noconfirm", *pkgs])
                if command_failed(result):
                    warnings.append(result)

        result = run_command(["sudo", "pacman", "-Sc", "--noconfirm"])
        if command_failed(result):
            warnings.append(result)

        result = run_command(["sudo", "journalctl", "--vacuum-time=2weeks"])
        if command_failed(result):
            warnings.append(result)

        for pattern in ("thumbnails", "mozilla/firefox"):
            cache_path = Path.home() / ".cache" / pattern
            if cache_path.exists():
                shutil.rmtree(cache_path, ignore_errors=True)

        if warnings:
            console.print("[yellow]Cleanup completed with warnings:[/yellow]")
            for warning in warnings:
                console.print(f"  [yellow]→[/yellow] {warning}")
        else:
            console.print("[green]✓ Cleanup completed[/green]")
    else:
        console.print("Aborted.")


@app.command()
def update() -> None:
    """Smart system update (pacman + AUR if available)."""
    console.print(Panel.fit("⬆️  System Update", style="bold green"))

    console.print("[cyan]Updating official packages...[/cyan]")
    result = run_command(["sudo", "pacman", "-Syu", "--noconfirm"])
    if command_failed(result):
        console.print(f"[red]Pacman update failed: {result}[/red]")
        raise typer.Exit(code=1)

    # Try AUR helpers
    for helper in ["yay", "paru"]:
        if shutil.which(helper):
            console.print(f"[cyan]Updating AUR packages with {helper}...[/cyan]")
            result = run_command([helper, "-Syu", "--noconfirm"])
            if command_failed(result):
                console.print(f"[red]AUR update failed: {result}[/red]")
                raise typer.Exit(code=1)
            break
    else:
        console.print("[yellow]No AUR helper found (yay/paru)[/yellow]")

    console.print("[green]✓ System update completed[/green]")


@app.command()
def search(query: str) -> None:
    """Search packages with better formatting."""
    console.print(Panel.fit(f"🔍 Searching for: [bold]{query}[/bold]", style="bold magenta"))

    output = run_command(["pacman", "-Ss", query])
    if not output or "Error" in output:
        console.print("[yellow]No results found.[/yellow]")
        return

    lines = output.split("\n")
    table = Table(show_header=True)
    table.add_column("Package", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            pkg_line = lines[i]
            desc_line = lines[i + 1]
            if "/" in pkg_line:
                pkg = pkg_line.split("/")[1].split(" ")[0]
                table.add_row(pkg, desc_line.strip())

    console.print(table)


@app.command()
def backup(
    output: Path = typer.Option(
        Path.home() / "backups/system-backup.tar.gz",
        "--output",
        "-o",
        help="Output archive path",
    ),
) -> None:
    """Create a backup of important system configs."""
    output.parent.mkdir(parents=True, exist_ok=True)

    console.print(Panel.fit(f"💾 Creating backup → [bold]{output}[/bold]", style="bold blue"))

    important_paths = [
        Path.home() / ".config",
        Path.home() / ".ssh",
        Path.home() / ".zshrc",
        Path.home() / ".gitconfig",
    ]
    existing_paths = [str(path) for path in important_paths if path.exists()]

    if not existing_paths:
        console.print("[red]Backup failed: no config paths found[/red]")
        raise typer.Exit(code=1)

    cmd = ["tar", "-czf", str(output), *existing_paths]
    result = run_command(cmd)

    if command_failed(result):
        console.print(f"[red]Backup failed: {result}[/red]")
        raise typer.Exit(code=1)

    size = output.stat().st_size / 1024 / 1024
    console.print(f"[green]✓ Backup created ({size:.1f} MB)[/green]")


@app.command()
def version() -> None:
    """Show syskit version."""
    console.print(f"syskit version: [bold cyan]{__version__}[/bold cyan]")


if __name__ == "__main__":
    app()
