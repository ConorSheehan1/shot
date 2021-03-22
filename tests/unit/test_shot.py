# Standard Library
import unittest
from unittest.mock import MagicMock, call, patch

# Third party
import pytest

# shot
from shot import Shot


class TestShot(unittest.TestCase):
    """
    Unit tests that don't hit file system at all. Calls are stubbed.
    """

    def setUp(self):
        # TODO: refactor, not all tests need isdir true for all args.
        # e.g. test_changing_extension_yes
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
        assert Shot(version=True)() == "1.0.0"

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

        s = Shot()
        s.console.print = MagicMock()

        s()
        s.console.print.assert_called_with(
            "Copied the following files from /tmp/tests to . successfully!\n['first']",
            style="green",
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

        s = Shot(quiet=True)
        s.console.print = MagicMock()

        assert s() == None
        # assert self.console.print was not called
        s.console.print.assert_has_calls([])
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

        assert Shot(dry_run=True)() == "cp /tmp/tests/first ."
        check_output_mock.assert_has_calls(check_output_calls)

    @patch("glob.glob")
    def test_src(self, glob_mock):
        glob_mock.side_effect = [["/tmp/some/other/path"]]

        assert Shot(src="/tmp/some/other/path", dry_run=True)() == "cp /tmp/some/other/path ."

    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_dst(self, check_output_mock, glob_mock):
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]

        assert Shot(dst="/tmp/output", dry_run=True)() == "cp /tmp/tests/first /tmp/output"

    @patch("glob.glob")
    @patch("subprocess.check_output")
    def test_move_dry_run(self, check_output_mock, glob_mock):
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first"]]

        assert Shot(mv=True, dry_run=True)() == "mv /tmp/tests/first ."

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

        s = Shot(mv=True)
        s.console.print = MagicMock()
        s()
        s.console.print.assert_called_with(
            "Moved the following files from /tmp/tests to . successfully!\n['first']", style="green"
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
        s = Shot()
        s.console.print = MagicMock()
        s()
        s.console.print.assert_called_with("No files found in /tmp/tests/empty", style="red")

    @patch("glob.glob")
    @patch("shutil.copy")
    @patch("subprocess.check_output")
    def test_not_enough_files_yes(self, check_output_mock, copy_mock, glob_mock):
        """
        should warn the user there are not enough files, but still copy the ones available
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/1"]]

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        copy_mock_calls = [call("/tmp/tests/1", ".")]
        print_mock_calls = [
            call("Warning: there are not enough files to copy with start:1, num:2", style="yellow"),
            call(
                "Copied the following files from /tmp/tests to . successfully!\n['1']",
                style="green",
            ),
        ]

        s = Shot(num=2, yes=True)
        s.console.print = MagicMock()
        s()
        s.console.print.assert_has_calls(print_mock_calls)
        check_output_mock.assert_has_calls(check_output_calls)
        copy_mock.assert_has_calls(copy_mock_calls)

    @patch("glob.glob")
    @patch("shutil.copy")
    @patch("subprocess.check_output")
    def test_changing_extension_yes(self, check_output_mock, copy_mock, glob_mock):
        """
        should warn the user the extension is being changed
        """
        # make sure dst is treated as file
        # self.mock_isdir.return_value = True
        self.mock_isdir.side_effect = [False, False]
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/first.txt"]]
        print_mock_calls = [
            call(
                "Warning: src and dst extensions don't match. src: .txt, dst: .md", style="yellow"
            ),
            call(
                "Copied the following files from /tmp/tests to ./first.md successfully!\n['first.txt']",
                style="green",
            ),
        ]

        copy_mock_calls = [call("/tmp/tests/first.txt", "./first.md")]
        s = Shot(yes=True, dst="./first.md")
        s.console.print = MagicMock()
        s()
        s.console.print.assert_has_calls(print_mock_calls)
        copy_mock.assert_has_calls(copy_mock_calls)

    @patch("glob.glob")
    @patch("shutil.copy")
    @patch("subprocess.check_output")
    def test_start_and_num(self, check_output_mock, copy_mock, glob_mock):
        """
        should copy the 2 latest screenshots, starting from the 2nd latest
        """
        check_output_mock.side_effect = [b"/tmp/tests\n"]
        glob_mock.side_effect = [["/tmp/tests/1", "/tmp/tests/2", "/tmp/tests/3", "/tmp/tests/4"]]

        check_output_calls = [call(["defaults", "read", "com.apple.screencapture", "location"])]
        copy_mock_calls = [call("/tmp/tests/2", "."), call("/tmp/tests/3", ".")]

        s = Shot(start=2, num=2)
        s.console.print = MagicMock()
        s()
        s.console.print.assert_called_with(
            "Copied the following files from /tmp/tests to . successfully!\n['2', '3']",
            style="green",
        )
        check_output_mock.assert_has_calls(check_output_calls)
        copy_mock.assert_has_calls(copy_mock_calls)


class TestShotErrorHandling(unittest.TestCase):
    def test_src(self):
        s = Shot(src="dir/that/does_not/exist")
        s.console.print = MagicMock()
        s()
        s.console.print.assert_called_with(
            "src must be a directory. got:dir/that/does_not/exist\n", style="red"
        )

    def test_dst(self):
        s = Shot(dst="dir/that/does_not/exist", num=2)
        s.console.print = MagicMock()
        s()
        s.console.print.assert_called_with(
            "dst must be a directory when num > 1. got:dir/that/does_not/exist\n", style="red"
        )

    def test_start(self):
        s = Shot(start=0)
        s.console.print = MagicMock()
        s()
        s.console.print.assert_called_with("start must be > 0. got:0\n", style="red")

    def test_num(self):
        s = Shot(num=0)
        s.console.print = MagicMock()
        s()
        s.console.print.assert_called_with("num must be > 0. got:0\n", style="red")

    def test_multiple_errors(self):
        """
        should show all errors together. don't make user find them one by one.
        note after #12 dst error is only raised when num > 1.
        e.g. num=1, dst can be file or directory. if not exists, will create file.
             num=2, dst must be directory.
        """
        s = Shot(num=0, start=0, dst="foo", src="foo")
        s.console.print = MagicMock()
        s()
        s.console.print.assert_called_with(
            "src must be a directory. got:foo\nstart must be > 0. got:0\nnum must be > 0. got:0\n",
            style="red",
        )
