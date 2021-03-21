# Standard Library
import glob
import os
import shutil
import subprocess
from typing import List

# Third party
import fire
from rich.console import Console
from rich.prompt import Prompt

commands = {"cp": "Copied", "mv": "Moved"}
__version__ = "1.0.0"


class Shot:
    """
    Screenshot Helper for OSX Terminal

    Args:
        src:      source directory. If None provided, find using apple defaults.  Default: None
        dst:      destination directory.                                          Default: .
        mv:       move the file instead of copying it.                            Default: False
        start:    file to start at. 1 = copy latest file. 2 = copy second latest. Default: 1
        num:      number of files to copy/move.                                   Default: 1
        yes:      answer yes to all prompts if True.                              Default: False
        color:    toggle color output.                                            Default: True
        quiet:    quiet mode, print less things to the console.                   Default: False
        dry_run:  if True show an equivalent bash command that would be run.      Default: False
        debug:    if True raise error with full stack trace, else print warning.  Default: False
        encoding: encoding to use for shell.                                      Default: utf-8
        version:  if True show version, else run shot.                            Default: False
    """

    def __init__(
        self,
        src: str = None,
        dst: str = ".",
        mv: bool = False,
        start: int = 1,
        num: int = 1,
        yes: bool = False,
        color: bool = True,
        quiet: bool = False,
        dry_run: bool = False,
        debug: bool = False,
        encoding: str = "utf-8",
        version: bool = False,
    ):
        self.src = src
        self.dst = dst
        self.mv = mv
        self.start = start
        self.num = num
        self.yes = yes
        self.color = color
        self.quiet = quiet
        self.dry_run = dry_run
        self.debug = debug
        self.encoding = encoding
        self.version = version

        color_system = "auto" if color else None
        self.console = Console(color_system=color_system)  # type: ignore

    def _get_shell_output(self, args: List[str]) -> str:
        # subprocess stdout is in bytes with trailing new line.
        # need to decode and strip to get string back.
        # e.g. b'700aa82a2b0c\n' -> '700aa82a2b0c'
        return subprocess.check_output(args).decode(self.encoding).strip()

    def _confirm(self) -> bool:
        return Prompt.ask("Do you want to continue?", choices=["y", "n"]) == "y"

    def _valid_extension(self, screenshot: str) -> bool:
        """
        return True if extension is not being changed, or user has chosen to change it.
        """
        if os.path.isdir(self.dst):
            return True

        src_ext, dst_ext = map(lambda x: os.path.splitext(x)[1], [screenshot, self.dst])
        if src_ext == dst_ext:
            return True

        self.console.print(
            f"Warning: src and dst extensions don't match. src: {src_ext}, dst: {dst_ext}",
            style="yellow",
        )

        return self.yes or self._confirm()  # if -y or users inputs y return True

    def _overwrite_file(self, screenshot: str) -> bool:
        """
        return True if file does not exist or user has chosen to overwrite it.
        """
        dst = os.path.join(self.dst, os.path.basename(screenshot))
        if not os.path.isfile(dst):
            return True

        self.console.print(f"Warning: {dst} already exists.", style="yellow")
        return self.yes or self._confirm()

    def _can_run_op(self, screenshot: str) -> bool:
        """
        return True if copy/move operation can be run, False if not
        """
        return self._valid_extension(screenshot) and self._overwrite_file(screenshot)

    def _validate_args(self) -> str:
        """
        returns error msg if there are errors, otherwise empty string
        """
        err_msg = ""
        if self.src:
            self.src = os.path.expanduser(self.src)
            if not os.path.isdir(self.src):
                err_msg += f"src must be a directory. got:{self.src}\n"
        self.dst = os.path.expanduser(self.dst)
        if self.num > 1 and not os.path.isdir(self.dst):
            err_msg += f"dst must be a directory when num > 1. got:{self.dst}\n"
        if self.start < 1:
            err_msg += f"start must be > 0. got:{self.start}\n"
        if self.num < 1:
            err_msg += f"num must be > 0. got:{self.num}\n"
        return err_msg

    def _valid_screenshots_to_copy(self):
        if len(self.screenshots_to_copy) < 1:
            self.console.print(f"No files found in {self.screenshot_dir_parsed}", style="red")
            return False
        if len(self.screenshots_to_copy) < self.num:
            self.console.print(
                f"Warning: there are not enough files to copy with start:{self.start}, num:{self.num}",
                style="yellow",
            )
            return self.yes or self._confirm()
        return True

    def __call__(self):
        if self.version:
            return __version__

        cmd = "mv" if self.mv else "cp"
        # TODO: move to 3.8, use walrus operator?
        err_msg = self._validate_args()
        if err_msg:
            return self.console.print(err_msg, style="red")

        if self.src:
            self.screenshot_dir = self.src
        else:
            self.screenshot_dir = self._get_shell_output(
                "defaults read com.apple.screencapture location".split()
            )

        self.screenshot_dir_parsed = os.path.expanduser(self.screenshot_dir)

        # all files in screenshots dir, sorted from newest to oldest
        all_screenshots = sorted(
            glob.glob(f"{self.screenshot_dir_parsed}/*"), key=os.path.getctime, reverse=True
        )
        self.screenshots_to_copy = all_screenshots[self.start - 1 : self.start + self.num - 1]
        if not self._valid_screenshots_to_copy():
            return False

        equivalent_command = " ".join([cmd, " ".join(self.screenshots_to_copy), self.dst])
        if self.dry_run:
            return equivalent_command

        try:
            for screenshot_to_copy in self.screenshots_to_copy:
                if not self._can_run_op(screenshot_to_copy):
                    return
                if cmd == "cp":
                    shutil.copy(screenshot_to_copy, self.dst)
                elif cmd == "mv":
                    shutil.move(screenshot_to_copy, self.dst)
                # no need for else, should be handled above by `if cmd not in accepted_cmds:`
            if not self.quiet:
                self.console.print(
                    f"{commands[cmd]} the following files to {self.dst} successfully!\n{self.screenshots_to_copy}",
                    style="green",
                )
        except Exception as e:
            self.console.print(f"{equivalent_command} failed", style="red")
            if self.debug:
                raise e
            raise SystemExit(1)


def main():
    fire.Fire(Shot)


if __name__ == "__main__":
    main()
