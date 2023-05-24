import pathlib
import subprocess


def _get_python_command():
    try:
        result = subprocess.run(
            ["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return "python"
    except FileNotFoundError:
        pass

    try:
        result = subprocess.run(
            ["python3", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return "python3"
    except FileNotFoundError:
        pass

    raise RuntimeError("No Python interpreter found")


class TextProcessor:
    """
    Class for preprocessing input file with external python script
    """

    def __init__(self):
        self.python_command = _get_python_command()

    def process(
        self,
        script_path: pathlib.Path,
        input_filepath: pathlib.Path,
        output_filepath: pathlib.Path,
    ) -> None:
        """
        Run external python script with input and output filepaths as arguments.
        Assumes that script reads input file and writes
        Arg
            script_path: path to python script
            input_filepath: path to input file
            output_filepath: path to output file
        """
        if script_path.suffix != ".py":
            raise ValueError(
                f"Script path must point to Python script, got {script_path}"
            )

        result = subprocess.run(
            [self.python_command, script_path, input_filepath, output_filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Script failed with error: {result.stderr.decode()}")
