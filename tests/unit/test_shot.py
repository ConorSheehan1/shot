# Standard Library
import unittest
from unittest.mock import call, patch

# Third party
from termcolor import colored

# shot
from shot import shot


class TestShot(unittest.TestCase):
    """
    Unit tests that don't hit file system at all. Calls are stubbed.
    """

    def setUp(self):
        self.isdir_patcher = patch("os.path.isdir")
        self.mock_isdir = self.isdir_patcher.start()
        self.mock_isdir.return_value = True
        self.addCleanup(self.isdir_patcher.stop)

        self.getctime_patcher = patch("os.path.getctime")
        self.mock_getctime = self.getctime_patcher.start()
        self.mock_getctime.return_value = 1  # keep original ordering
        self.addCleanup(self.getctime_patcher.stop)

    def test_version(self):
        """
        should return the version
        """
        assert shot(version=True) == "1.0.0"

    @patch("glob.glob")
    @patch("shutil.copy")
    @patch("subprocess.check_output")
    def test_default_args(self, check_output_mock, copy_mock, glob_mock):
        """
        should copy the latest screenshot to the current directory
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        copy_mock_calls = [call("/tmp/tests/first", ".")]

        assert shot() == colored(
            "Copied the following files to . successfully!\n['/tmp/tests/first']", "green"
        )
        check_output_mock.assert_has_calls(check_output_calls)
        copy_mock.assert_has_calls(copy_mock_calls)

    @patch("glob.glob")
    @patch("shutil.copy")
    @patch("subprocess.check_output")
    def test_quiet(self, check_output_mock, copy_mock, glob_mock):
        """
        should copy the latest screenshot to the current directory, without printing any messages
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        copy_mock_calls = [call("/tmp/tests/first", ".")]

        assert shot(quiet=True) == None
        check_output_mock.assert_has_calls(check_output_calls)
        copy_mock.assert_has_calls(copy_mock_calls)

    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_dry_run(self, check_output_mock, glob_mock):
        """
        should show the command that would copy the latest screenshot to the current directory
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]

        assert shot(dry_run=True) == "cp /tmp/tests/first ."
        check_output_mock.assert_has_calls(check_output_calls)

    @patch("glob.glob")
    def test_src(self, glob_mock):
        glob_mock.side_effect = [["/tmp/some/other/path"]]

        assert shot(src="/tmp/some/other/path", dry_run=True) == "cp /tmp/some/other/path ."

    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_dst(self, check_output_mock, glob_mock):
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]

        assert shot(dst="/tmp/output", dry_run=True) == "cp /tmp/tests/first /tmp/output"

    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_move_dry_run(self, check_output_mock, glob_mock):
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]

        assert shot(mv=True, dry_run=True) == "mv /tmp/tests/first ."

    @patch("glob.glob")
    @patch("shutil.move")
    @patch("subprocess.check_output")
    def test_move(self, check_output_mock, move_mock, glob_mock):
        """
        should move the latest screenshot to the current directory
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        move_mock_calls = [call("/tmp/tests/first", ".")]

        assert (
            shot(mv=True, color=False)
            == "Moved the following files to . successfully!\n['/tmp/tests/first']"
        )
        check_output_mock.assert_has_calls(check_output_calls)
        move_mock.assert_has_calls(move_mock_calls)

    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_no_files(self, check_output_mock, glob_mock):
        """
        should warn the user no files were found
        """
        check_output_mock.side_effect = [b"/tmp/tests/empty\n"]
        glob_mock.side_effect = [[]]

        assert shot(color=False) == "No files found in /tmp/tests/empty"

    @patch("builtins.print")  # note print interferes with termcolor somehow, use color=False
    @patch("glob.glob")
    @patch("shutil.copy")
    @patch("subprocess.check_output")
    def test_not_enough_files_yes(self, check_output_mock, copy_mock, glob_mock, print_mock):
        """
        should warn the user there are not enough files, but still copy the ones available
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/1"]]

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        copy_mock_calls = [call("/tmp/tests/1", ".")]
        print_mock_calls = [
            call(
                colored("Warning: there are not enough files to copy with start:0, num:1", "yellow")
            )
        ]

        assert (
            shot(num=2, color=False, yes=True)
            == "Copied the following files to . successfully!\n['/tmp/tests/1']"
        )
        check_output_mock.assert_has_calls(check_output_calls)
        copy_mock.assert_has_calls(copy_mock_calls)

    @patch("glob.glob")
    @patch("shutil.copy")
    @patch("subprocess.check_output")
    def test_s_and_n(self, check_output_mock, copy_mock, glob_mock):
        """
        should copy the 2 latest screenshots, starting from the 2nd latest
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/1", "/tmp/tests/2", "/tmp/tests/3", "/tmp/tests/4"]]

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        copy_mock_calls = [call("/tmp/tests/2", "."), call("/tmp/tests/3", ".")]

        assert (
            shot(start=2, num=2, color=False)
            == "Copied the following files to . successfully!\n['/tmp/tests/2', '/tmp/tests/3']"
        )
        check_output_mock.assert_has_calls(check_output_calls)
        copy_mock.assert_has_calls(copy_mock_calls)


class TestShotErrorHandling(unittest.TestCase):
    def test_src(self):
        assert (
            shot(src="dir/that/does_not/exist", color=False)
            == "src must be a directory. got:dir/that/does_not/exist\n"
        )

    def test_dst(self):
        assert (
            shot(dst="dir/that/does_not/exist", num=2, color=False)
            == "dst must be a directory. got:dir/that/does_not/exist\n"
        )

    def test_s(self):
        assert shot(start=0, color=False) == "start must be > 0. got:0\n"

    def test_n(self):
        assert shot(num=0, color=False) == "num must be > 0. got:0\n"

    def test_multiple_errors(self):
        """
        should show all errors together. don't make user find them one by one.
        note after #12 dst error is only raised when num > 1.
        e.g. num=1, dst can be file or directory. if not exists, will create file.
             num=2, dst must be directory.
        """
        assert (
            shot(num=0, start=0, dst="foo", src="foo", color=False)
            == "src must be a directory. got:foo\nstart must be > 0. got:0\nnum must be > 0. got:0\n"
        )
