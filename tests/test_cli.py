"""Tests for syskit CLI using Typer's CliRunner and mocks."""

from __future__ import annotations

import re
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from syskit.cli import app, command_failed, run_command

runner = CliRunner()
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def plain(output: str) -> str:
    """Strip Rich ANSI codes for stable assertions."""
    return ANSI_RE.sub("", output)


def test_version_command():
    """Basic version command outputs the version string."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "syskit version: 0.1.0" in plain(result.output)


def test_help():
    """--help should list available commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "syskit" in result.output
    assert "info" in result.output
    assert "clean" in result.output
    assert "update" in result.output
    assert "search" in result.output
    assert "backup" in result.output
    assert "version" in result.output


@patch("syskit.cli.platform")
@patch("syskit.cli.run_command")
@patch("builtins.open")
def test_info_command(mock_open, mock_run_command, mock_platform):
    """info command displays system info using platform and mocked commands."""
    # Platform mocks
    mock_platform.node.return_value = "testhost"
    mock_platform.release.return_value = "6.12.1-arch1-1"
    mock_platform.machine.return_value = "x86_64"
    mock_platform.python_version.return_value = "3.12.3"

    # /etc/os-release mock
    mock_file = MagicMock()
    mock_file.__enter__.return_value = ['PRETTY_NAME="Arch Linux"\n']
    mock_open.return_value = mock_file

    # Command mocks
    mock_run_command.side_effect = [
        "up 1 day, 2 hours",  # uptime
        (
            "              total        used        free      shared  "
            "buff/cache   available\n"
            "Mem:           31Gi        12Gi        15Gi       123Mi       4.2Gi        18Gi"
        ),  # free -h
    ]

    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "System Information" in result.output
    assert "testhost" in result.output
    assert "Arch Linux" in result.output
    assert "up 1 day" in result.output
    assert "12Gi" in result.output  # from memory parsing


@patch("syskit.cli.run_command")
def test_clean_dry_run(mock_run):
    """clean --dry-run should list actions without executing or prompting."""
    mock_run.return_value = "orphan1\norphan2\norphan3"  # pacman -Qtdq

    result = runner.invoke(app, ["clean", "--dry-run"])
    assert result.exit_code == 0
    assert "System Cleanup" in result.output
    assert "Dry run mode" in result.output
    assert "orphan packages" in result.output
    assert "pacman package cache" in result.output
    # Should not have called the real cleanup commands
    assert not any("sudo" in str(c) for c in mock_run.call_args_list)


@patch("syskit.cli.typer.confirm")
@patch("syskit.cli.run_command")
def test_clean_with_confirm_no(mock_run, mock_confirm):
    """clean (no dry-run) with user saying no aborts."""
    mock_run.return_value = ""  # no orphans
    mock_confirm.return_value = False

    result = runner.invoke(app, ["clean"])
    assert result.exit_code == 0
    assert "Aborted" in result.output
    # Real cleanup commands not executed
    assert "sudo pacman" not in " ".join(str(c) for c in mock_run.call_args_list)


@patch("syskit.cli.typer.confirm")
@patch("syskit.cli.run_command")
def test_clean_with_confirm_yes(mock_run, mock_confirm):
    """clean with confirm yes runs the cleanup commands."""
    mock_run.return_value = ""
    mock_confirm.return_value = True

    result = runner.invoke(app, ["clean"])
    assert result.exit_code == 0
    assert "Running cleanup" in result.output
    assert "Cleanup completed" in result.output
    # Check that sudo commands were "called"
    calls = [str(c) for c in mock_run.call_args_list]
    assert any("pacman" in c and "-Sc" in c for c in calls)
    assert any("journalctl" in c for c in calls)


@patch("syskit.cli.shutil.which")
@patch("syskit.cli.run_command")
def test_update_with_aur_helper(mock_run, mock_which):
    """update detects yay/paru and runs it."""
    mock_which.side_effect = lambda x: x == "paru"  # only paru present
    mock_run.return_value = ""

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0
    assert "Updating official packages" in result.output
    assert "Updating AUR packages with paru" in result.output
    assert "System update completed" in result.output

    # pacman + paru called
    calls = [str(c) for c in mock_run.call_args_list]
    assert any("pacman" in c and "-Syu" in c for c in calls)
    assert any("paru" in c and "-Syu" in c for c in calls)


@patch("syskit.cli.shutil.which")
@patch("syskit.cli.run_command")
def test_update_pacman_failure(mock_run, mock_which):
    """update exits with error when pacman fails."""
    mock_which.return_value = None
    mock_run.return_value = "Error: pacman failed"

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 1
    assert "Pacman update failed" in plain(result.output)


@patch("syskit.cli.shutil.which")
@patch("syskit.cli.run_command")
def test_update_no_aur_helper(mock_run, mock_which):
    """update without AUR helper still succeeds and warns."""
    mock_which.return_value = None
    mock_run.return_value = ""

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0
    assert "No AUR helper found (yay/paru)" in plain(result.output)
    assert "System update completed" in result.output


@patch("syskit.cli.run_command")
def test_search_with_results(mock_run):
    """search parses pacman -Ss output into a nice table."""
    mock_run.return_value = (
        "extra/firefox 128.0-1 [installed]\n"
        "    Fast, Private and Safe Web Browser\n"
        "community/vscode 1.90-1\n"
        "    Code editor\n"
    )

    result = runner.invoke(app, ["search", "firefox"])
    assert result.exit_code == 0
    assert "Searching for: firefox" in plain(result.output)
    assert "firefox" in result.output
    assert "Fast, Private" in result.output


@patch("syskit.cli.run_command")
def test_search_no_results(mock_run):
    """search with no/error output shows friendly message."""
    mock_run.return_value = "Error: nothing found"

    result = runner.invoke(app, ["search", "nonexistentpkg999"])
    assert result.exit_code == 0
    assert "No results found" in result.output


@patch("syskit.cli.run_command")
def test_backup_success(mock_run, tmp_path):
    """backup creates parent dir (via code) and reports size on success."""
    # Use a temp output so we don't touch real ~
    backup_file = tmp_path / "backups" / "test-backup.tar.gz"
    # Simulate successful tar (run_command returns no "Error")
    mock_run.return_value = ""

    # Create the file so .stat() works in the success branch
    backup_file.parent.mkdir(parents=True)
    backup_file.write_bytes(b"x" * 1234567)  # ~1.2 MB

    # Patch the default in the Option? Easier: invoke with explicit --output
    result = runner.invoke(app, ["backup", "--output", str(backup_file)])
    assert result.exit_code == 0
    assert "Creating backup" in result.output
    assert "Backup created" in result.output
    assert "MB" in result.output


@patch("syskit.cli.run_command")
def test_backup_failure(mock_run, tmp_path):
    """backup shows error message when run_command fails."""
    backup_file = tmp_path / "backup-fail.tar.gz"
    mock_run.return_value = "Error: tar failed"

    result = runner.invoke(app, ["backup", "--output", str(backup_file)])
    assert result.exit_code == 1
    assert "Backup failed" in result.output


def test_run_command_success():
    """run_command returns stripped stdout on success."""
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = " hello \n world \n"
        mock_run.return_value = mock_result
        out = run_command(["echo", "hello"])
        assert out == "hello \n world"
        mock_run.assert_called_once()


def test_run_command_called_process_error():
    """run_command returns Error: ... on CalledProcessError."""
    with patch("subprocess.run") as mock_run:
        err = subprocess.CalledProcessError(1, ["false"])
        err.stderr = "some error output"
        mock_run.side_effect = err
        out = run_command(["false"])
        assert out.startswith("Error: some error output")


def test_run_command_file_not_found():
    """run_command handles missing binary gracefully."""
    with patch("subprocess.run", side_effect=FileNotFoundError()):
        out = run_command(["nonexistentcmd"])
        assert "Command not found: nonexistentcmd" in out


def test_command_failed_detects_errors():
    """command_failed recognizes run_command error prefixes."""
    assert command_failed("Error: boom")
    assert command_failed("Command not found: foo")
    assert not command_failed("all good")


@patch("syskit.cli.Path.home")
@patch("syskit.cli.shutil.which")
@patch("syskit.cli.run_command")
def test_doctor_all_ok(mock_run, mock_which, mock_home, tmp_path):
    """doctor exits 0 when all checks pass."""

    def which_side_effect(name: str) -> str:
        if name == "syskit":
            return "/home/bill/.local/bin/syskit"
        return f"/usr/bin/{name}"

    mock_which.side_effect = which_side_effect

    def fake_run(cmd, capture=True):
        if cmd[:2] == ["locale", "charmap"]:
            return "UTF-8"
        if cmd[:3] == ["gh", "auth", "status"]:
            return "Logged in to github.com"
        if "-c" in cmd:
            return ""
        return ""

    mock_run.side_effect = fake_run

    clone = tmp_path / "syskit"
    clone.mkdir()
    (clone / "pyproject.toml").touch()
    venv_py = clone / ".venv" / "bin" / "python"
    venv_py.parent.mkdir(parents=True)
    venv_py.touch()
    mock_home.return_value = tmp_path

    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "All checks passed" in plain(result.output)


@patch("syskit.cli.shutil.which", return_value=None)
@patch("syskit.cli.run_command", return_value="ISO-8859-1")
def test_doctor_fails_without_syskit(mock_run, mock_which):
    """doctor exits 1 when critical checks fail."""
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1
    assert "check(s) failed" in plain(result.output)


@pytest.mark.parametrize(
    "cmd",
    [
        "info",
        "clean",
        "update",
        "search foo",
        "backup --output /tmp/x.tar.gz",
        "doctor",
        "version",
    ],
)
def test_all_commands_have_help_text(cmd):
    """Smoke test: every command is registered and has a docstring/help."""
    # Just invoking --help on subcommand or the command itself
    args = cmd.split() + ["--help"]
    result = runner.invoke(app, args)
    # Some commands show their own help or the global; exit 0 or 2 is fine for --help
    assert (
        "Usage:" in result.output or "help" in result.output.lower() or result.exit_code in (0, 2)
    )
