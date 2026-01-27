#!/usr/bin/env python3
"""
CLI launcher for the project microTPCT
Author: Basile Bergeron, Meredith Biteau, Ambre Bordas, Noé Cursimaux, Ambroise Loeb
This module defines the CLI options, input validation, and execution
logic for running the microTPCT matching pipeline.
"""

import click,  subprocess, sys #type: ignore

from datetime import datetime
from typing import List, Tuple, Literal, Dict
from pathlib import Path
from yaspin import yaspin #type: ignore
from yaspin.spinners import Spinners #type: ignore

from microtpct.core.pipeline import run_pipeline

# Message helpers
def echo_info(msg: str):
    click.echo(f"[INFO] {msg}")

def echo_error(msg: str):
    click.echo(f"[ERROR] {msg}", err=True)

# Pipeline execution wrapper
class PipelineRunner:
    WILDCARD_CHOICES = ["B", "X", "Z", "J", "U", "O", "-", ".", "?"]

    def __init__(
        self,
        query_input,
        target_input,
        algo="aho",
        wildcards=(),
        output=None,
        log=None,
        err=None,
        ext="csv",
        tf=None,
        qf=None,
        ts=None,
        qs=None,
        name=""
    ):
        """
        Initialize a PipelineRunner instance.

        Parameters
        ----------
        query_input : str or Path
            Path to the query input file.
        target_input : str or Path
            Path to the target input file.
        algo : str
            Matching algorithm to use.
        wildcards : tuple
            Allowed wildcard characters.
        output : Path or None
            Output directory.
        log : bool
            Enable logging of stdout.
        err : bool
            Enable logging of stderr.
        ext : str
            Output file extension.
        tf, qf : str or None
            Target and query input formats.
        ts, qs : str or None
            Target and query field separators.
        name : str
            Analysis name.
        """
        self.query_input = Path(query_input)
        self.target_input = Path(target_input)
        self.algo = algo
        self.wildcards = wildcards
        self.output_path = output if output else Path.cwd().resolve()
        self.ext = ext
        self.log = log
        self.err = err
        self.tf = tf
        self.qf = qf
        self.ts = ts
        self.qs = qs
        self.analyse_name = name

    # Validation
    @staticmethod
    def validate_input_file(file_path: str | Path) -> str | Path:
        """
        Validate that the given path exists and is a file.

        Raises
        ------
        click.BadParameter
            If the file does not exist or is not a file.
        """
        path = Path(file_path)
        if not path.exists():
            raise click.BadParameter(f"File not found: {file_path}")
        if not path.is_file():
            raise click.BadParameter(f"Not a file: {file_path}")
        return path.resolve()

    @staticmethod
    def validate_algo_flags(algo_flags: List[Tuple[str, bool]]) -> str:
        """
        Ensure that at most one algorithm flag is selected.

        Parameters
        ----------
        algo_flags : list of (str, bool)
            Algorithm names with activation flags.

        Returns
        -------
        str
            Selected algorithm name.

        Raises
        ------
        click.UsageError
            If more than one algorithm is selected.
        """
        selected = [name for name, active in algo_flags if active]
        if len(selected) > 1:
            raise click.UsageError("Please select only one algorithm")
        return selected[0] if selected else "aho"

    @staticmethod
    def _timestamp():
        return datetime.now()

    def manage_output_path(self) -> None:
        ts = self._timestamp()
        self.result_file = self.output_path / f"microtpct_matching_result_{ts.strftime("%Y%m%d_%H%M%S")}.{self.ext}"
        self.stats_file  = self.output_path / f"microtpct_statistics_{ts.strftime("%Y%m%d_%H%M%S")}.{self.ext}"
        return

    def format_wildcard(self) -> None:
        """
        Normalize wildcard configuration.

        Enables wildcard processing if at least one wildcard is provided.
        Defaults to 'X' if no wildcard is specified.
        """

        self.wildcard_flag = bool(self.wildcards)
        self.wildcards = list(self.wildcards) if self.wildcard_flag else ["X"]
    
    def format_output_format(self) -> None:
        """Ensure a valid output file extension is defined."""
        self.ext = self.ext if self.ext else "csv"

    def log_managment(self) -> None :
        """Configure log output path if logging is enabled."""
        if self.log:
            self.log_path = self.output_path
        else :
            self.log_path = None
    
    def err_managment(self) -> None :
        """Configure error output path if error logging is enabled."""
        if self.err:
            self.err_path = self.output_path
        else :
            self.err_path = None


    # Pipeline execution
    def launch_pipeline(self):
        """
        Prepare configuration and execute the microTPCT pipeline.
        """

        self.timestamp = self._timestamp()

        # Formats input
        self.manage_output_path()
        self.format_output_format()
        self.format_wildcard()

        self.log_managment()
        self.err_managment()

        
        echo_info(
            f" Target_input        :{self.target_input}\n\t"
            f"Query_input         :{self.query_input}\n\t"
            f"Target format       :{self.tf}\n\t"
            f"Query format        :{self.qf}\n\t"
            f"Target separator    :{self.ts}\n\t"
            f"Query separato      :{self.qs}\n\t"
            f"output_path         :{self.output_path}\n\t"
            f"Output format       :{self.ext}\n\t"
            f"Analyse name        :{self.analyse_name}\n\t"
            f"log_path            :{self.log_path}\n\t"
            f"err_path            :{self.err_path}\n\t"
            f"wildcard_flag       :{self.wildcard_flag}\n\t"
            f"wildcards           :{self.wildcards}\n\t"
            f"Matching engine     :{self.algo}\n\n")

        run_pipeline(
            self.target_input,
            self.query_input,
            target_format = self.tf,
            query_format = self.qf,
            target_separator = self.ts,
            query_separator = self.qs,
            output_path = self.output_path,
            output_format = self.ext,
            analysis_name = self.analyse_name,
            log_file =  self.log_path, 
            allow_wildcard = self.wildcard_flag,
            wildcards = self.wildcards,
            matching_engine = self.algo
        )

    # Start (install dependencies)
    @staticmethod
    def start(requirements_file: Path | None = None):
        """
        Install project dependencies from the requirements file.

        This method is intended to be used via the --start CLI option.
        """

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
    # Next line in to force WILDCARD_CHOICES to --allow_wildcard input
    #type=click.Choice(PipelineRunner.WILDCARD_CHOICES, case_sensitive=True),
    type=str,
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
@click.option("--log", is_flag=True, help="Write all stdout to FILE")
@click.option("--err", is_flag=True, help="Write all error to FILE")
@click.option("--usage",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=usage_callback,
    help="Install dependencies and exit",
)
@click.option("--job_name", type=str, help="Specify the analysis name")

# OI option
@click.option("-o", "--output",
              type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
              help="Output directory")
@click.option("--ext",
    type=click.Choice(["csv", "xlsx"], case_sensitive=False),
    help="Specify output file format [csv/xlsx]")
@click.option("--tf",type=str, help="Specify target file format")
@click.option("--qf",type=str, help="Specify query file format")
@click.option("--ts",type=str, help="Specify target file separator (if csv/xlsx/tsv...)")
@click.option("--qs",type=str, help="Specify target file separator (if csv/xlsx/tsv...)")


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
    ext: str,
    log: bool,
    err: bool,
    query_input: str | Path,
    target_input: str | Path,
    job_name: str,
    tf: str ,
    qf: str ,
    ts: str ,
    qs: str 
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
        err=err,
        ext=ext,
        name=job_name,
        tf=tf,
        qf=qf,
        ts=ts,
        qs=qs
    )
    runner.launch_pipeline()



# Entry point
if __name__ == "__main__":
    cli(prog_name="microTPCT")
