import sys
import unittest

from src.application.common import Environment


class TestEnvironment(unittest.TestCase):
    def test_file_memory_limit_set_via_env(self):
        environment = Environment.from_env({"IN_MEMORY_FILE_SIZE": "1000"})
        self.assertEqual(1000, environment.in_memory_file_limit)

    def test_get_os(self):
        environment = Environment.from_env({})
        self.assertEqual(
            environment.os,
            "linux" if sys.platform in {"linux", "linux2"} else "windows",
        )
