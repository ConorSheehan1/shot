# Standard Library
import glob
import os
import shutil
import subprocess
from typing import List

# Third party
import fire
import termcolor

commands = {"cp": "Copied", "mv": "Moved"}
__version__ = "0.1.2"


def _get_shell_output(args: List[str], encoding: str) -> str:
    # subprocess stdout is in bytes with trailing new line. need to decode and strip to get string back.
    # e.g. b'700aa82a2b0c\n' -> '700aa82a2b0c'
    return subprocess.check_output(args).decode(encoding).strip()


def shot(
    src: str = None,
    dst: str = ".",
    mv: bool = False,
    s: int = 1,
    n: int = 1,
    color: bool = True,
    q: bool = False,
    dry_run: bool = False,
    debug: bool = False,
    encoding: str = "utf-8",
    version: bool = False,
):
    """
    Screenshot Helper for OSX Terminal

    Args:
        src:      source directory. If None provided, find using apple defaults. Default: None
        dst:      destination directory.                                         Default: .
        mv:       move the file instead of copying it.                           Default: False
        s:        start at sth latest file, 1-indexed.                           Default: 1
        n:        number of files to copy/move:                                  Default: 1
        color:    toggle color output.                                           Default: True
        q:        quiet mode, print less things to the console.                  Default: False
        dry_run:  if True show an equivalent command that would be run.          Default: False
        debug:    raise error with full stack trace. otherwise print warning.    Default: False
        encoding: encoding to use for shell.                                     Default: utf-8
        version:  if True show version, else run shot.                           Default: False
    """
    if version:
        return __version__

    if not color:
        termcolor.colored = lambda message, color: message  # type: ignore

    cmd = "mv" if mv else "cp"

    err_msg = ""

    if src:
        src = os.path.expanduser(src)
        if not os.path.isdir(src):
            err_msg += f"src must be a directory. got:{src}\n"

    dst = os.path.expanduser(dst)
    if not os.path.isdir(dst):
        err_msg += f"dst must be a directory. got:{dst}\n"

    if s < 1:
        err_msg += f"s must be > 0. got:{s}\n"
    if n < 1:
        err_msg += f"n must be > 0. got:{n}\n"

    if err_msg:
        return termcolor.colored(err_msg, "red")

    if src:
        screenshot_dir = src
    else:
        screenshot_dir = _get_shell_output(
            "defaults read com.apple.screencapture location".split(), encoding
        )

    screenshot_dir_parsed = os.path.expanduser(screenshot_dir)

    # all files in screenshots dir, sorted from newest to oldest
    all_screenshots = sorted(
        glob.glob(f"{screenshot_dir_parsed}/*"), key=os.path.getctime, reverse=True
    )
    screenshots_to_copy = all_screenshots[s - 1 : s + n - 1]

    if len(screenshots_to_copy) < 1:
        return termcolor.colored(f"No files found in {screenshot_dir_parsed}", "red")

    if len(screenshots_to_copy) < n:
        print(
            termcolor.colored(
                f"Warning: there are not enough files to copy with s:{s}, n:{n}", "yellow"
            )
        )

    equivalent_command = " ".join([cmd, " ".join(screenshots_to_copy), dst])
    if dry_run:
        return equivalent_command

    success_msg = termcolor.colored(
        f"{commands[cmd]} the following files to {dst} successfully!\n{screenshots_to_copy}",
        "green",
    )
    err_msg = termcolor.colored(f"{equivalent_command} failed", "red")

    try:
        for screenshot_to_copy in screenshots_to_copy:
            if cmd == "cp":
                shutil.copy(screenshot_to_copy, dst)
            elif cmd == "mv":
                shutil.move(screenshot_to_copy, dst)
            # no need for else, should be handled above by `if cmd not in accepted_cmds:`
        if not q:
            return success_msg
    except Exception as e:
        print(err_msg)
        if debug:
            raise e
        else:
            raise SystemExit(1)


def main():
    fire.Fire(shot)


if __name__ == "__main__":
    main()
