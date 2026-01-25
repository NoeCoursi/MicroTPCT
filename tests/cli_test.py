# tests/test_cli_complete.py
import pytest
import subprocess
from pathlib import Path
import sys
from click.testing import CliRunner
from microtpct.interfaces.cli import cli, start

# ----------------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------------
@pytest.fixture
def temp_files(tmp_path):
    """Crée des fichiers FASTA temporaires pour query et target"""
    query = tmp_path / "query.fasta"
    target = tmp_path / "target.fasta"
    query.write_text(">query\nACDEFGHIKLMNPQRSTVWY")
    target.write_text(">target\nACDEFGHIKLMNPQRSTVWY")
    return query, target, tmp_path

@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / "out"

# ----------------------------------------------------------------------
# HELPER POUR LANCER LA CLI
# ----------------------------------------------------------------------
def run_cli(args, input_text=None):
    """Exécute le CLI via Click CliRunner et retourne (exit_code, stdout, stderr)"""
    runner = CliRunner()
    result = runner.invoke(cli, args, input=input_text)
    return result.exit_code, result.output, result.exception

# ----------------------------------------------------------------------
# TESTS DES ALGORITHMES
# ----------------------------------------------------------------------
@pytest.mark.parametrize("algo_flag,expected", [
    (["--aho"], "aho"),
    (["--bm"], "bm"),
    (["--ag"], "ag"),
    (["--blast"], "blast"),
    (["--regex"], "regex"),
])
def test_individual_algos(algo_flag, expected, temp_files):
    query, target, _ = temp_files
    code, out, err = run_cli(algo_flag + [str(query), str(target)])
    assert code == 1  # pipeline non exécuté
    assert f"Algo   : {expected}" in out
    assert "LANCEMENT PIPELINE" in out

def test_default_algo(temp_files):
    query, target, _ = temp_files
    code, out, err = run_cli([str(query), str(target)])
    assert code == 1
    assert "Algo   : aho" in out

def test_multiple_algos_error(temp_files):
    query, target, _ = temp_files
    code, out, err = run_cli(["--aho", "--bm", str(query), str(target)])
    assert code != 0
    assert "Please select only one algorithm" in (out + str(err))

# ----------------------------------------------------------------------
# TEST ALLOW_WILDCARD
# ----------------------------------------------------------------------
def test_allow_wildcard_multiple(temp_files):
    query, target, _ = temp_files
    code, out, err = run_cli(["--allow_wildcard", "X", "--allow_wildcard", "B", str(query), str(target)])
    assert code == 1
    assert "Wildcards selected: ('X', 'B')" in out

def test_allow_wildcard_invalid(temp_files):
    query, target, _ = temp_files
    code, out, err = run_cli(["--allow_wildcard", "Q", str(query), str(target)])
    assert code != 0
    assert "Invalid value for '--allow_wildcard'" in (out + str(err))

# ----------------------------------------------------------------------
# TEST OUTPUT & LOG / ERR
# ----------------------------------------------------------------------
def test_output_dir_creation(temp_files, output_dir):
    query, target, _ = temp_files
    code, out, err = run_cli(["--aho", "-o", str(output_dir), str(query), str(target)])
    assert code == 1
    assert output_dir.exists() and output_dir.is_dir()
    assert f"Output : {output_dir}" in out

def test_log_err_files(temp_files, output_dir):
    query, target, _ = temp_files
    if output_dir :
        output_dir.mkdir()
        code, out, err = run_cli([
            "--aho", "-o", str(output_dir), "--log", "--err",
            str(query), str(target)
        ])
        assert code == 1
        assert (output_dir / "stdout.log").exists()
        assert (output_dir / "stdout.err").exists()
    else :
        return

# ----------------------------------------------------------------------
# TEST START
# ----------------------------------------------------------------------
def test_start_confirmed(monkeypatch):
    monkeypatch.setattr("click.confirm", lambda *a, **k: True)
    monkeypatch.setattr("microtpct.interfaces.cli.start", lambda: print("START CALLED"))
    code, out, err = run_cli(["--start"])
    assert code == 0
    assert "START CALLED" in out

def test_start_cancelled(monkeypatch):
    monkeypatch.setattr("click.confirm", lambda *a, **k: False)
    code, out, err = run_cli(["--start"])
    assert code == 0
    assert "Installation abordted." in out


# ----------------------------------------------------------------------
# TEST VALIDATION DES FICHIERS
# ----------------------------------------------------------------------
def test_invalid_query_file(temp_files):
    _, target, tmp_path = temp_files
    missing = tmp_path / "missing.fasta"
    code, out, err = run_cli(["--aho", str(missing), str(target)])
    assert code != 0
    assert f"File not found: {missing}" in (out + str(err))

def test_invalid_target_file(temp_files):
    query, _, tmp_path = temp_files
    missing = tmp_path / "missing.fasta"
    code, out, err = run_cli(["--aho", str(query), str(missing)])
    assert code != 0
    assert f"File not found: {missing}" in (out + str(err))
