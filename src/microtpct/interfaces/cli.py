#!/usr/bin/env python3
"""
Professional CLI launcher for the project microTPCT
Author: Meredith, Ambre, Ambroise, Noe, Basile
"""

import click  # type: ignore
from pathlib import Path

from contextlib import redirect_stdout, redirect_stderr, ExitStack
from yaspin import yaspin  # type: ignore
from yaspin.spinners import Spinners  # type: ignore

#from microtpct.core import run_pipeline # type: ignore


# ----------------------------
# Message helpers
# ----------------------------
def echo_info(msg):
    click.echo(f"[INFO] {msg}")

def echo_error(msg):
    click.echo(f"[ERROR] {msg}", err=True)


# ----------------------------
# Validate input files
# ----------------------------
def validate_input_file(ctx, param, value):
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"File not found: {value}")
    if not path.is_file():
        raise click.BadParameter(f"Not a file: {value}")
    return path.resolve()

# Start option managment
def start_callback(ctx, param, value):
    if not value:  # <-- Ignore si --start n'est pas présent
        return
    click.echo(
        click.style(
            "Warning:\n"
            "option --start is used to install dependencies.\n"
            "No other action will be computed and options and inpu files will be ignored\n"
            "Use option -h o --help for more informations",
            fg="yellow",
            bold=True,
        )
    )

    if not click.confirm("\nContinue ?", default=True):
        click.echo("Installation aborted.")
        ctx.exit(0)

    start()
    ctx.exit(0)




# ----------------------------
# Algo and wildcard mangament 
# ----------------------------
def validate_algo(ctx, aho, bm, ag, blast, regex):
    algo_flags = [("aho", aho), ("bm", bm), ("ag", ag), ("blast", blast), ("regex", regex)]
    selected = [name for name, active in algo_flags if active]

    if len(selected) > 1:
        echo_error("Please select only one algorithm")
        ctx.exit(1)
    elif len(selected) == 0:
        matching_engine = "aho"  # default
    else:
        matching_engine = selected[0]
    return matching_engine

def validate_wildcards(ctx, allow_wildcard):
    print("Wildcards selected:", allow_wildcard)



# ----------------------------
# Main CLI
# ----------------------------
@click.command(
    context_settings=dict(ignore_unknown_options=False, allow_extra_args=True)
)

# Algo choice
@click.option("--aho", is_flag=True, help="Use Aho–Corasick algorithm (default)")
@click.option("--bm", is_flag=True, help="Use Boyer-Moore algorithm")
@click.option("--ag", is_flag=True, help="Use AWK-GREP algorithm")
@click.option("--blast", is_flag=True, help="Use BLAST algorithm")
@click.option("--regex", is_flag=True, help="Use regex-based matching (not recommended)")

@click.option(
    "--allow_wildcard",
    multiple=True,
    type=click.Choice(["B", "X", "Z", "J", "U", "O", "-", ".", "?"], case_sensitive=True),
    help="Allows wildcards processing (choose from [B,X,Z,J,U,O,-,.,?])")

# General options
@click.option(
    "--start",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=start_callback,
    help="Install dependencies and exit",
)
    
#TODO : link to docs / USAGE.txt path 
#@click.option("-h","--help", is_flag=True, help="Install dependencies and exit")
@click.option("-o", "--output",
              type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
              help="Output directory")

@click.option("--log",is_flag=True,help="Write all stdout to FILE",)
@click.option("--err",is_flag=True,help="Write all error to FILE",)
@click.option("--usage",is_flag=True,help="Write all error to FILE",)

@click.argument("query_input", callback=validate_input_file)
@click.argument("target_input", callback=validate_input_file)
@click.version_option(version="1.0.0", prog_name="microTPCT")
@click.pass_context
def cli(ctx, aho, bm, ag, blast, regex, allow_wildcard, output, log, err, usage, query_input, target_input):
    """
    CLI entry point for microTPCT
    """
    ctx.ensure_object(dict)
    
    # print USAGE.txt as helper
    if usage:
        usage_file = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "USAGE.txt"
        print(usage_file)
        if usage_file.exists():
            click.echo(usage_file.read_text())
        else:
            click.echo("USAGE.txt not found!")
        ctx.exit(0)

    # Determine algorithm
    matching_engine = validate_algo(ctx, aho, bm, ag, blast, regex)

    # Wildcard managment
    validate_wildcards(ctx, allow_wildcard)

    # Output directory
    if output:
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
    if not output:
        output_path = Path.cwd()

    # General option managment
    #if help:
        #TODO cat PATH(__resolve()__).parent.parent.parent / "docs" / USAGE.txt
    #    ctx.exit(1)



    # ----------------------------
    # Display info
    # ----------------------------
    #echo_info(f"[{matching_engine.upper()}] Query={query_input}, Target={target_input}")
    print("\n")
    print(f"Algo   : {matching_engine}")
    print(f"Output : {output_path}")
    print(f"allow_wildcard : {allow_wildcard}")
    print(f"Query  : {query_input}")
    print(f"Target : {target_input}")

    print("LANCEMENT PIPELINE")
    # ----------------------------
    # Call your pipeline here
    # ----------------------------

    with ExitStack() as stack:
        if log:
            log_path = output_path / "stdout.log"
            log_f = stack.enter_context(open(log_path, "w"))
            stack.enter_context(redirect_stdout(log_f))

        if err:
            err_path = output_path / "stdout.err"
            err_f = stack.enter_context(open(err_path, "w"))
            stack.enter_context(redirect_stderr(err_f))

        print(matching_engine, allow_wildcard, output_path, query_input, target_input)
        exit(1)
        """
        run_pipeline(
            target_input: PathLike,                 # OK
            query_input: PathLike,                  # OK
            target_format: str | None = None,         
            query_format: str | None = None,
            target_separator: str | None = None,
            query_separator: str | None = None,
            output: PathLike | None = None,         # OK
            output_format: Literal["excel", "csv"] = "csv",
            analysis_name: str | None = None,
            log_file: PathLike | None = None,       # OK
            allow_wildcard: bool = True,            # OK
            wildcards: str | List[str] = "X", 
            matching_engine: str = "aho",           # OK
        )"""



# ----------------------------
# Optional command to install dependencies
# ----------------------------
def start():
    import sys
    import subprocess
    requirements_file = Path(__file__).resolve().parent.parent.parent / "requirements.txt"
    print("Installing dependencies from:", requirements_file)
    exit(1)  # Remove this line when ready to actually install
    with yaspin(Spinners.dots, text="Installing dependencies...") as spinner:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--user", "-r", str(requirements_file)]
            )
            spinner.ok("Dependencies installed")
            echo_info("microTPCT is ready to use!")
        except subprocess.CalledProcessError as e:
            spinner.fail("Error while installing dependencies")
            echo_error(f"Failed to install dependencies: {e}")
            sys.exit(1)


# ----------------------------
# Entry point
# ----------------------------
if __name__ == "__main__":
    cli(prog_name="microTPCT")