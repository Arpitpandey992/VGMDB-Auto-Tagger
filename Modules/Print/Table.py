from typing import Any
from pydantic import BaseModel
from rich.console import Console, JustifyMethod, OverflowMethod
from rich.align import VerticalAlignMethod
from rich.table import Table


class Column(BaseModel):
    header: str = ""
    footer: str = ""
    header_style: str | None = None
    footer_style: str | None = None
    style: str | None = None
    justify: JustifyMethod = "left"
    vertical: VerticalAlignMethod = "top"
    overflow: OverflowMethod = "ellipsis"
    width: int | None = None
    min_width: int | None = None
    max_width: int | None = None
    ratio: int | None = None
    no_wrap: bool = False


def tabulate(
    table_data: list[tuple[Any, ...]],
    *,
    columns: tuple[Column, ...] | None = None,
    add_number_column: bool = False,
    title: str | None = None,
    **kwargs: Any,
):
    show_header = any(column.header for column in columns) if columns else False
    show_footer = any(column.footer for column in columns) if columns else False
    table = Table(title=title, title_justify="right", show_header=show_header, show_footer=show_footer, **kwargs)
    if columns:
        if add_number_column:
            columns = (Column(header="S.No.", justify="center", style="bold"),) + columns
        for column in columns:
            table.add_column(**column.model_dump())
    for i, data in enumerate(table_data):
        cleaned_data = [str(val) for val in data if data]
        if add_number_column:
            cleaned_data.insert(0, str(i + 1))
        table.add_row(*cleaned_data)
    console = Console()
    console.print(table)


def test():
    table_data = [
        ("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690"),
        ("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347"),
        ("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889"),
        ("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889"),
    ]
    columns = (
        Column(header="Released", header_style="bold on yellow italic", justify="center", style="on cyan bold", no_wrap=True),
        Column(header="Title", style="magenta on white"),
        Column(header="Box Office", justify="left", style="green italic"),
    )
    tabulate(table_data, columns=columns, title="Star Wars Movies", padding=(1, 2))  # note that i provided padding here even though it is not part of the function arg


if __name__ == "__main__":
    table = test()
