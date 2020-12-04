# Standard Library
import unittest
from unittest.mock import call, patch

# shot
from shot import shot


class TestShot(unittest.TestCase):
    def test_version(self):
        """
        should return the version
        """
        assert shot(version=True) == "0.1.0"

    @patch("os.path.getctime")
    @patch("glob.glob")
    @patch("subprocess.run")
    @patch("subprocess.check_output")
    def test_shot_default_args(self, check_output_mock, run_mock, glob_mock, getctime_mock):
        """
        should copy the latest screenshot to the current directory
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]
        getctime_mock.returns(1)

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        run_mock_calls = [call(["cp", "/tmp/tests/first", "."])]

        shot()
        check_output_mock.assert_has_calls(check_output_calls)
        run_mock.assert_has_calls(run_mock_calls)

    @patch("os.path.getctime")
    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_shot_dry_run(self, check_output_mock, glob_mock, getctime_mock):
        """
        should show the command that would copy the latest screenshot to the current directory
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]
        getctime_mock.returns(1)

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]

        assert shot(dry_run=True) == "cp /tmp/tests/first ."
        check_output_mock.assert_has_calls(check_output_calls)

    @patch("os.path.isdir")
    @patch("os.path.getctime")
    @patch("glob.glob")
    def test_shot_src(self, glob_mock, getctime_mock, isdir_mock):
        isdir_mock.returns(True)
        glob_mock.side_effect = [["/tmp/some/other/path"]]
        getctime_mock.returns(1)

        assert shot(src="/tmp/some/other/path", dry_run=True) == "cp /tmp/some/other/path ."

    @patch("os.path.isdir")
    @patch("os.path.getctime")
    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_shot_dest(self, check_output_mock, glob_mock, getctime_mock, isdir_mock):
        isdir_mock.returns(True)
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]
        getctime_mock.returns(1)

        assert shot(dest="/tmp/output", dry_run=True) == "cp /tmp/tests/first /tmp/output"