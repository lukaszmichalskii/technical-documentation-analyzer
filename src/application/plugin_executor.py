import pathlib
import subprocess
import sys


def execute_plugin(
    script_path: pathlib.Path,
    input_filepath: pathlib.Path,
    output_filepath: pathlib.Path,
):
    """
    Run external python script with input and output filepaths as arguments.
    Assumes that script reads input file and writes
    Arg
        script_path: path to python script
        input_filepath: path to input file
        output_filepath: path to output file
    """
    if script_path.suffix != ".py":
        raise ValueError(f"Script path must point to Python script, got {script_path}")

    result = subprocess.run(
        [sys.executable, script_path, input_filepath, output_filepath],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Script failed with error: {result.stderr.decode()}")
