#!/usr/bin/env python3
"""
Professional CLI launcher for the project microTPCT
Author: Meredith, Ambre, Ambroise, Noe, Basile
"""

from pathlib import Path
import click #type: ignore

from pathlib import Path
from yaspin import yaspin #type: ignore
from yaspin.spinners import Spinners #type: ignore

from microtpct.core import pipeline



# Message helpers
def echo_info(msg):
    click.echo(f"[INFO] {msg}")

def echo_error(msg):
    click.echo(f"[ERROR] {msg}", err=True)



# Main CLI
@click.group(invoke_without_command=True, context_settings=dict(ignore_unknown_options=True))
@click.option("-h", "--help", is_flag=True, help="Show detailed help (from docs/USAGE.txt)")
@click.version_option(version="1.0.0", prog_name="microTPCT")
@click.pass_context
def cli(ctx, help):
    """
    CLI entry point for microTPCT
    """
    ctx.ensure_object(dict)

    # Custom help using docs/USAGE.txt
    if help:
        usage_path = Path(__file__).resolve().parent.parent.parent / "docs" / "USAGE.txt"
        if usage_path.exists():
            click.echo(usage_path.read_text())
        else:
            click.echo("[USAGE.TXT] file not found!")
        ctx.exit()

    if ctx.invoked_subcommand is None:
        click.echo("No command provided. Use -h or --help for help.")




# Define type commands dynamically
type_commands = [
    ("aho", "Perform Aho–Corasick based peptide matching (default)"),
    ("bm", "Perform Boyer-Moore based peptide matching"),
    ("ag", "Perform AWk-GREP based peptide matching"),
    ("blast", "Perform BLAST-based peptide matching"),
    ("regex", "Perform regex-based peptide matching (not recommended)"),
]

for cmd_name, cmd_help in type_commands:
    def make_cmd(name=cmd_name, help_text=cmd_help):
        @cli.command(name=name, help=help_text)
        @click.argument("query_input")
        @click.argument("target_input")
        @click.pass_context
        def command(ctx, query_input, target_input):
            echo_info(f"[{name.upper()}] Query={query_input}, Target={target_input}")
        
            pipeline(ctx, query_input, target_input)

        return command
    make_cmd()



# Command: start
@cli.command(help="Start microTPCT and install dependencies")
def start():
    import sys
    import subprocess
    requirements_file = Path(__file__).resolve().parent.parent.parent / "requirements.txt"
    print("Installing dep")
    print("Exit project")
    exit(1)
    with yaspin(Spinners.dots, text="Installing dependencies...") as spinner:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-r", str(requirements_file)])
            spinner.ok("Dependencies installed")
            echo_info("microTPCT is ready to use!")
        except subprocess.CalledProcessError as e:
            spinner.fail("Error while installing dependencies")
            echo_error(f"Failed to install dependencies: {e}")
            sys.exit(1)



# Entry point
if __name__ == "__main__":
    cli(prog_name="microTPCT")
