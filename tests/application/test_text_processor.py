import subprocess
import unittest
from unittest.mock import patch
import tempfile
import pathlib
from src.application.text_processor import TextProcessor


class TestTextProcessor(unittest.TestCase):

    @patch("subprocess.run")
    def test_process(self, mock_subprocess):
        mock_subprocess.return_value.returncode = 0

        temp_dir = tempfile.TemporaryDirectory()
        script_path = pathlib.Path(temp_dir.name) / "script.py"
        input_filepath = pathlib.Path(temp_dir.name) / "input.txt"
        output_filepath = pathlib.Path(temp_dir.name) / "output.txt"

        # Create dummy files for testing
        script_path.touch()
        input_filepath.touch()
        output_filepath.touch()

        processor = TextProcessor()
        processor.process(script_path, input_filepath, output_filepath)

        mock_subprocess.assert_called_with(
            [processor.python_command, script_path, input_filepath, output_filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Cleanup
        temp_dir.cleanup()

    def test_process_script_not_python(self):
        temp_dir = tempfile.TemporaryDirectory()
        script_path = pathlib.Path(temp_dir.name) / "script.txt"
        input_filepath = pathlib.Path(temp_dir.name) / "input.txt"
        output_filepath = pathlib.Path(temp_dir.name) / "output.txt"

        # Create dummy files for testing
        script_path.touch()
        input_filepath.touch()
        output_filepath.touch()

        processor = TextProcessor()
        with self.assertRaises(ValueError):
            processor.process(script_path, input_filepath, output_filepath)

        # Cleanup
        temp_dir.cleanup()
