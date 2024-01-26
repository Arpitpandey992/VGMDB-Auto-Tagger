from rich.console import Console

console = Console()


def get_rich_console():
    """maintain the use of a single rich console throughtout"""
    return console
