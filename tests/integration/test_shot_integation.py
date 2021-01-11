# Standard Library
import os
import unittest

# shot
from shot import shot


# TODO: try https://docs.pytest.org/en/latest/tmpdir.html
class TestShot(unittest.TestCase):
    """
    Integration tests do no stub function. Runs calls that hit file system.
    """

    def setUp(self):
        self.expected_output_path = os.path.join("tests", "fixtures", "dst", "foo.txt")

    def tearDown(self):
        # clean up output after tests
        if os.path.exists(self.expected_output_path):
            os.remove(self.expected_output_path)

    def test_copy(self):
        self.assertFalse(os.path.exists(self.expected_output_path))
        shot(src="tests/fixtures/src", dst="tests/fixtures/dst")
        self.assertTrue(os.path.exists(self.expected_output_path))

    def test_debug_cp_file_exists(self):
        """
        should fail because src and dest are the same.
        latest file will be foo, will fail to copy since it already exists.
        """
        with self.assertRaises(Exception) as context:
            shot(src="tests/fixtures/src", dst="tests/fixtures/src", debug=True)

        self.assertIn(
            "'tests/fixtures/src/foo.txt' and 'tests/fixtures/src/foo.txt' are the same file",
            context.exception.args,
        )

    def test_debug_mv_file_exists(self):
        """
        should fail because src and dest are the same.
        latest file will be foo, will fail to copy since it already exists.
        """
        with self.assertRaises(Exception) as context:
            shot(src="tests/fixtures/src", dst="tests/fixtures/src", mv=True, debug=True)

        self.assertIn(
            "Destination path 'tests/fixtures/src/foo.txt' already exists", context.exception.args
        )
