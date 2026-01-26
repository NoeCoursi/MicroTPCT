#!/usr/bin/env python3
"""
CLI launcher for the project microTPCT
Author: Basile Bergeron, Meredith Biteau, Ambre Bordas, Noé Cursimaux, Ambroise Loeb
"""

import click,  subprocess, sys #type: ignore

from typing import List, Tuple, Literal, Dict
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr, ExitStack
from yaspin import yaspin #type: ignore
from yaspin.spinners import Spinners #type: ignore


# Message helpers
def echo_info(msg: str):
    click.echo(f"[INFO] {msg}")

def echo_error(msg: str):
    click.echo(f"[ERROR] {msg}", err=True)

# Core Pipeline class
class PipelineRunner:
    WILDCARD_CHOICES = ["B", "X", "Z", "J", "U", "O", "-", ".", "?"]

    def __init__(self, query_input, target_input, algo="aho",
                 wildcards=(), output=None, log=False, err=False):
        self.query_input = Path(query_input)
        self.target_input = Path(target_input)
        self.algo = algo
        self.wildcards = wildcards
        self.output_path = Path(output) if output else Path.cwd()
        self.log = log
        self.err = err

        # Create output directory if it doesn't exist
        self.output_path.mkdir(parents=True, exist_ok=True)

    # Validation
    @staticmethod
    def validate_input_file(file_path: str | Path) -> str | Path:
        path = Path(file_path)
        if not path.exists():
            raise click.BadParameter(f"File not found: {file_path}")
        if not path.is_file():
            raise click.BadParameter(f"Not a file: {file_path}")
        return path.resolve()

    @staticmethod
    def validate_algo_flags(algo_flags: List[Tuple[str, bool]]) -> str:
        selected = [name for name, active in algo_flags if active]
        if len(selected) > 1:
            raise click.UsageError("Please select only one algorithm")
        return selected[0] if selected else "aho"

    
    # ----------------------------
    # Pipeline execution
    # ----------------------------
    def run_pipeline(self):
        """Print info and simulate pipeline execution"""
        print("\n")
        print(f"Algo   : {self.algo}")
        print(f"Output : {self.output_path}")
        print(f"allow_wildcard : {self.wildcards}")
        print(f"Query  : {self.query_input}")
        print(f"Target : {self.target_input}")
        print("LANCEMENT PIPELINE")

        with ExitStack() as stack:
            if self.log:
                log_path = self.output_path / "stdout.log"
                log_f = stack.enter_context(open(log_path, "w"))
                stack.enter_context(redirect_stdout(log_f))

            if self.err:
                err_path = self.output_path / "stdout.err"
                err_f = stack.enter_context(open(err_path, "w"))
                stack.enter_context(redirect_stderr(err_f))

            # TODO replace with actual call
            print(self.algo, self.wildcards, self.output_path,
                  self.query_input, self.target_input)

            exit(1)


    # Start (install dependencies)
    @staticmethod
    def start(requirements_file: Path | None = None):
        requirements_file = Path(__file__).resolve().parent.parent.parent.parent / "requirements.txt"
        print("Installing dependencies from:", requirements_file)
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

# called start_callback and usage_callback called before cli
# if --start or --usage are parsed

def start_callback(ctx: click.Context, param: click.Parameter, value):
    """
    Executed start() if --start is used to install dependencies
    No pipeline is launched
    """
    if not value:
        return
    click.echo(
        click.style(
            "Warning:\n"
            "option --start is used to install dependencies.\n"
            "No other action will be computed and input files will be ignored\n"
            "Use option -h or --help for more informations",
            fg="yellow",
            bold=True,
        )
    )
    if not click.confirm("\nContinue ?", default=True):
        click.echo("Installation aborted.")
        ctx.exit(0)

    PipelineRunner.start()
    ctx.exit(0)

def usage_callback(ctx: click.Context, param: click.Parameter, value):
    """
    Print docs/USAGE.txt if --usage is used
    No pipeline is launched
    """
    if not value:
        return

    usage_file = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "USAGE.txt"
    if usage_file.exists():
        click.echo(usage_file.read_text())
    else:
        click.echo("USAGE.txt not found!")
    ctx.exit(0)



# Main CLI
@click.command(
    context_settings=dict(ignore_unknown_options=False, allow_extra_args=True)
)
# Algorithm choice
@click.option("--aho", is_flag=True, help="Use Aho–Corasick algorithm (default)")
@click.option("--bm", is_flag=True, help="Use Boyer-Moore algorithm")
@click.option("--ag", is_flag=True, help="Use AWK-GREP algorithm")
@click.option("--blast", is_flag=True, help="Use BLAST algorithm")
@click.option("--regex", is_flag=True, help="Use regex-based matching (not recommended)")
@click.option("--find", is_flag=True, help="Use native python .find() matching")

# Wildcards
@click.option("--allow_wildcard",
    multiple=True,
    type=click.Choice(PipelineRunner.WILDCARD_CHOICES, case_sensitive=True),
    help="Allows wildcards processing (choose from [B,X,Z,J,U,O,-,.,?])"
)

# General options
@click.option("--start",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=start_callback,
    help="Install dependencies and exit",
)
@click.option("-o", "--output",
              type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
              help="Output directory")
@click.option("--log", is_flag=True, help="Write all stdout to FILE")
@click.option("--err", is_flag=True, help="Write all error to FILE")
@click.option("--usage",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=usage_callback,
    help="Install dependencies and exit",
)

# Arguments
@click.argument("query_input",
    callback=lambda ctx, param,
    val: PipelineRunner.validate_input_file(val))
@click.argument("target_input",callback=lambda ctx, param, val: PipelineRunner.validate_input_file(val))
@click.version_option(version="1.0.0", prog_name="microTPCT")
@click.pass_context
def cli(
    ctx: click.Context,
    aho: bool,
    bm: bool,
    ag: bool,
    blast: bool,
    regex: bool,
    find: bool,
    allow_wildcard: Tuple[str, ...],
    output: str | Path,
    log: bool,
    err: bool,
    query_input: str | Path,
    target_input: str | Path,
) -> None:
    
    """
    CLI entry point for microTPCT
    """
    ctx.ensure_object(dict)

    # ----------------------------
    # Determine algorithm
    # ----------------------------
    algo_flags = [("aho", aho), ("bm", bm), ("ag", ag), ("blast", blast), ("regex", regex), ("find", find)]
    algo = PipelineRunner.validate_algo_flags(algo_flags)

    # ----------------------------
    # Run pipeline
    # ----------------------------
    runner = PipelineRunner(
        query_input=query_input,
        target_input=target_input,
        algo=algo,
        wildcards=allow_wildcard,
        output=output,
        log=log,
        err=err
    )
    runner.run_pipeline()



# Entry point
if __name__ == "__main__":
    cli(prog_name="microTPCT")
