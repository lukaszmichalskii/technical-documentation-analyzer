import sys
import unittest

import application.common


class TestEnvironment(unittest.TestCase):
    def test_file_memory_limit_set_via_env(self):
        environment = application.common.Environment.from_env(
            {"IN_MEMORY_FILE_SIZE": "1000"}
        )
        self.assertEqual(1000, environment.in_memory_file_limit)

    def test_get_os(self):
        environment = application.common.Environment.from_env({})
        self.assertEqual(
            environment.os,
            "linux" if sys.platform in {"linux", "linux2"} else "windows",
        )
