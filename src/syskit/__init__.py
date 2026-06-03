"""syskit - Modern CLI toolkit for Arch/Manjaro users."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("syskit")
except PackageNotFoundError:
    # Fallback during development when not installed
    __version__ = "0.1.0"
