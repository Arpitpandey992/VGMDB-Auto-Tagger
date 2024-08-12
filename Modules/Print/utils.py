from typing import Any
from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel

console = Console()


def get_rich_console():
    """maintain the use of a single rich console throughout"""
    return console


def print_separator():
    """prints a wide line to separate sections"""
    get_rich_console().print(Rule(style="white", characters="━"))


def get_panel(text: str, *args: Any, expand: bool = False, **kwargs: Any) -> Panel:
    return Panel(text, *args, expand=expand, **kwargs)
