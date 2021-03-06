# Standard Library
import glob
import os
import shutil
import subprocess
from typing import List

# Third party
import fire
import termcolor  # TODO: replace termcolor with rich
from rich.prompt import Prompt

commands = {"cp": "Copied", "mv": "Moved"}
__version__ = "1.0.0"


def _confirm() -> bool:
    return Prompt.ask("Do you want to continue?", choices=["y", "n"]) == "y"


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

    def _get_shell_output(self, args: List[str]) -> str:
        # subprocess stdout is in bytes with trailing new line.
        # need to decode and strip to get string back.
        # e.g. b'700aa82a2b0c\n' -> '700aa82a2b0c'
        return subprocess.check_output(args).decode(self.encoding).strip()

    # TODO: test _confirm_extension
    def _confirm_extension(self, screenshot) -> bool:
        if os.path.isdir(self.dst):
            return True

        src_ext, dst_ext = map(lambda x: os.path.splitext(x)[1], [screenshot, self.dst])
        if src_ext == dst_ext:
            return True

        print(
            termcolor.colored(
                f"src and dst extensions don't match. src: {src_ext}, dst: {dst_ext}", "yellow"
            )
        )
        return _confirm()

    def _validate_args(self) -> str:
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

    def _validate_screenshots_to_copy(self):
        if len(self.screenshots_to_copy) < 1:
            return termcolor.colored(f"No files found in {self.screenshot_dir_parsed}", "red")
        if len(self.screenshots_to_copy) < self.num:
            print(
                termcolor.colored(
                    f"Warning: there are not enough files to copy with start:{self.start}, num:{self.num}",
                    "yellow",
                )
            )
            if not self.yes and not _confirm():
                return True
        return False

    def __call__(self):
        if self.version:
            return __version__

        if not self.color:
            termcolor.colored = lambda message, color: message  # type: ignore

        cmd = "mv" if self.mv else "cp"
        # TODO: move to 3.8, use walrus operator?
        err_msg = self._validate_args()
        if err_msg:
            return termcolor.colored(err_msg, "red")

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
        screenshot_err = self._validate_screenshots_to_copy()
        if screenshot_err:
            return screenshot_err

        equivalent_command = " ".join([cmd, " ".join(self.screenshots_to_copy), self.dst])
        if self.dry_run:
            return equivalent_command

        success_msg = termcolor.colored(
            f"{commands[cmd]} the following files to {self.dst} successfully!\n{self.screenshots_to_copy}",
            "green",
        )
        err_msg = termcolor.colored(f"{equivalent_command} failed", "red")

        try:
            for screenshot_to_copy in self.screenshots_to_copy:
                if not self._confirm_extension(screenshot_to_copy):
                    return
                if cmd == "cp":
                    shutil.copy(screenshot_to_copy, self.dst)
                elif cmd == "mv":
                    shutil.move(screenshot_to_copy, self.dst)
                # no need for else, should be handled above by `if cmd not in accepted_cmds:`
            if not self.quiet:
                return success_msg
        except Exception as e:
            print(err_msg)
            if self.debug:
                raise e
            raise SystemExit(1)


def main():
    fire.Fire(Shot)


if __name__ == "__main__":
    main()
