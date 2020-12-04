# Standard Library
import unittest
from unittest.mock import call, patch

# shot
from shot import shot


class TestShot(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("os.path.isdir")
        self.mock_isdir = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_version(self):
        """
        should return the version
        """
        assert shot(version=True) == "0.1.0"

    @patch("os.path.getctime")
    @patch("glob.glob")
    @patch("shutil.copy")
    @patch("subprocess.check_output")
    def test_shot_default_args(self, check_output_mock, copy_mock, glob_mock, getctime_mock):
        """
        should copy the latest screenshot to the current directory
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]
        getctime_mock.returns(1)

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        copy_mock_calls = [call("/tmp/tests/first", ".")]

        shot()
        check_output_mock.assert_has_calls(check_output_calls)
        copy_mock.assert_has_calls(copy_mock_calls)

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

    @patch("os.path.getctime")
    @patch("glob.glob")
    def test_shot_src(self, glob_mock, getctime_mock):
        glob_mock.side_effect = [["/tmp/some/other/path"]]
        getctime_mock.returns(1)

        assert shot(src="/tmp/some/other/path", dry_run=True) == "cp /tmp/some/other/path ."

    @patch("os.path.getctime")
    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_shot_dst(self, check_output_mock, glob_mock, getctime_mock):
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]
        getctime_mock.returns(1)

        assert shot(dst="/tmp/output", dry_run=True) == "cp /tmp/tests/first /tmp/output"


class TestShotErrorHandling(unittest.TestCase):
    def test_n(self):
        assert shot(n=0, color=False) == "n must be > 0. got:0\n"

    def test_s(self):
        assert shot(s=0, color=False) == "s must be > 0. got:0\n"

    def test_src(self):
        assert (
            shot(src="dir/that/does_not/exist", color=False)
            == "src must be a directory. got:dir/that/does_not/exist\n"
        )

    def test_dst(self):
        assert (
            shot(dst="dir/that/does_not/exist", color=False)
            == "dst must be a directory. got:dir/that/does_not/exist\n"
        )

    def test_multiple_errors(self):
        """
        should show all errors together. don't make user find them one by one
        """
        assert (
            shot(n=0, s=0, dst="foo", src="foo", color=False)
            == "src must be a directory. got:foo\ndst must be a directory. got:foo\nn must be > 0. got:0\ns must be > 0. got:0\n"
        )
