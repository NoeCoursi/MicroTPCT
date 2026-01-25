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

def check_dependencies(ctx, start) :
    if start and ctx.args:
        echo_error("`--start` must be used alone. Use: microTPCT --start")
        ctx.exit(1)

    if start:
        start()
        return
    
def check_start_exclusive(opts):
    if opts.get("start"):
        # Liste des options à tester (flags mutuellement exclusifs avec start)
        other_flags = ["aho", "bm", "ag", "blast", "regex", "allow_wildcard", "output", "log", "err"]
        for key in other_flags:
            value = opts.get(key)
            # Pour les bools et tuples/lists, check if set / non-empty
            if isinstance(value, bool) and value:
                return False
            if isinstance(value, (tuple, list)) and len(value) > 0:
                return False
            if value not in (None, False, (), []):
                return False
        return True
    return None

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

@click.option("--start", is_flag=True, help="Install dependencies and exit")
#TODO : link to docs / USAGE.txt path 
#@click.option("-h","--help", is_flag=True, help="Install dependencies and exit")
@click.option("-o", "--output",
              type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
              help="Output directory")

@click.option("--log",type=click.Path(dir_okay=False, writable=True),help="Write all stdout to FILE",)
@click.option("--err",type=click.Path(dir_okay=False, writable=True),help="Write all error to FILE",)

@click.argument("query_input", callback=validate_input_file)
@click.argument("target_input", callback=validate_input_file)
@click.version_option(version="1.0.0", prog_name="microTPCT")
@click.pass_context
def cli(ctx, aho, bm, ag, blast, regex, allow_wildcard, start, output, log, err, query_input, target_input):
    """
    CLI entry point for microTPCT
    """
    ctx.ensure_object(dict)
    
    # Install dependencies if option --start is TRUE
    #check_dependencies(ctx, start)

    # Check if option --start is alone
    is_startexclusive = check_start_exclusive(dict(ctx.params))
    
    if is_startexclusive is True:
        print("Executing --start command")
        start()
        ctx.exit(0)  # ou exit(0) si pas de ctx
    elif is_startexclusive is False:
        print("--start must be used alone")
        ctx.exit(1)

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
