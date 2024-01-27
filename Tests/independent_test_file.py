from enum import Enum
import os
import random
import re
from urllib.parse import urlparse


def is_date_in_YYYY_MM_DD(date: list[str]) -> bool:
    if not date:
        return False
    pattern = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$")
    return bool(pattern.match(date[0]))


print(is_date_in_YYYY_MM_DD(["2034-07-25"]))
print(is_date_in_YYYY_MM_DD(["1990-12-31"]))
print(is_date_in_YYYY_MM_DD(["2007-14-14"]))
print(is_date_in_YYYY_MM_DD(["2023-06-00"]))
print(is_date_in_YYYY_MM_DD(["2034-45"]))
print(is_date_in_YYYY_MM_DD(["2034"]))
print(is_date_in_YYYY_MM_DD(["2453-00-00"]))


path = "/home/arpit/Downloads/music/myAmazingAlbum/Disc 01 - Julius Caesar/Et tu, brute?.flac"
dir_name = os.path.dirname(path)
disc_name = os.path.basename(os.path.normpath(dir_name))
file_name = os.path.basename(os.path.normpath(path))
print(disc_name)
print(file_name)
print(os.path.basename(os.path.dirname(os.path.normpath(path))))


url = "https://i0.wp.com/www.alphr.com/wp-content/uploads/2021/04/Screenshot_9-26.png?resize=396%2C382&ssl=1"
parsed_url = urlparse(url)
print(parsed_url.path)
x = os.path.splitext(os.path.basename(parsed_url.path))

import wcwidth


def my_rjust(text, width):
    return " " * max(0, (width - wcwidth.wcswidth(text))) + text


print("\nThe problem:")
text = "世界您好"
print(f"Chinese: {text:>30}|")
text = "หวัดดีชาวโลก"
print(f"   Thai: {text:>30}|")
text = "Hello world."
print(f"English: {text:>30}|")

print("\nUsing wcwidth:")
text = "世界您好"
print(f"Chinese: {my_rjust(text, 30)}|")
text = "หวัดดีชาวโลก"
print(f"   Thai: {my_rjust(text, 30)}|")
text = "Hello world."
print(f"English: {my_rjust(text, 30)}|")

print("{:>8s}".format("ありがとう"))
print("{:\u3000>8s}".format("ありがとう"))


x = [1, 2, 3]
y = []
z = [val for val in y[:1]]
z.extend(val for val in x)
print(z)

from tabulate import tabulate

table_data = [(x, 234, "dafasd", 1) for x in range(1, 20)]
table_data.sort()
print(tabulate(table_data))
print("\n")
table_data = [(str(x), 1) for x in range(1, 20)]
table_data.sort()
print(tabulate(table_data))

"""main.py"""
from tap import Tap


class Args(Tap):
    package: str
    is_cool: bool = True
    stars: int = 5


args = Args().parse_args(["--package", "Tap"])

args_data = args.as_dict()
print(args_data)  # {'package': 'Tap', 'is_cool': True, 'stars': 5}

args_data["damn"] = 2000
args = args.from_dict(args_data)
print(args.damn)  # 2000

s = set([1, 2, 3])
t = set([1, 3, 4, 5, 6])
print(s - t)


def func():
    str = "damn son"
    if True:
        str = "why Son"
    print(str)


func()


from rich.console import Console
from rich.table import Table

table = Table(title="Star Wars Movies")

table.add_column("Released", justify="right", style="cyan", no_wrap=True)
table.add_column("Title", style="magenta")
table.add_column("Box Office", justify="right", style="green")

table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889")
table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889")
table.add_row("ddddd", "世界您好", "$1,332,439,889")
table.add_row("Dec 16, 2016", "หวัดดีชาวโลก", "$1,332,439,889")

console = Console()
console.print(table)

# from rich.prompt import Prompt

# name = Prompt.ask("Enter your name", choices=["Paul", "Jessica", "Duncan"], default="Paul")


import requests


try:
    requests.get("http://localhost:8081")
except Exception as e:
    print(e)
    print(type(e))
    # raise e

a = [1, 2, 3]
b = ["1", "2", "3"]
print(a + b)
print(a)
c = (1, 2)
d = ("1", "2")

print(c + d)
c = c + d
print(c)


import questionary

choices = ["damn", questionary.Choice("son", checked=True)]

questionary.checkbox("damn son?", choices=choices)


class common_choices(Enum):
    yes = "Yes"
    no = "No"
    go_back = "Go Back"
    edit_configs = "Edit Configs"


print(common_choices.yes)


conf = False
x = f"Title{' [Translated]' if conf else ''}"
print(x)

from rich.console import Console
from rich.panel import Panel

panel = Panel("Organizing", expand=False)

# Print the box with content
console.print(
    panel,
)


from rich.console import Console
from rich.rule import Rule

console = Console()

# Print some text
console.print("This is line 1")
console.print("This is line 2")

# Print a line separator
console.print(Rule(style="white"))

# Print more text after the separator
console.print("This is line 3")
console.print("This is line 4")

from rich.console import Console
import time

# Create a Console instance
console = Console()

# Initial status
with console.status("[bold]Working...[/bold]"):
    # Simulate some work
    time.sleep(2)

with console.status("[bold green]Done![/bold green]"):
    time.sleep(2)
