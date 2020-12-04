# Standard Library
import glob
import os
import shutil
import subprocess
from typing import List

# Third party
import fire
from termcolor import colored

commands = {"cp": "Copied", "mv": "Moved"}
__version__ = "0.1.0"


def _get_shell_output(args: List[str], encoding: str) -> str:
    # subprocess stdout is in bytes with trailing new line. need to decode and strip to get string back.
    # e.g. b'700aa82a2b0c\n' -> '700aa82a2b0c'
    return subprocess.check_output(args).decode(encoding).strip()


def shot(
    cmd: str = "cp",
    src: str = None,
    dst: str = ".",
    s: int = 1,
    n: int = 1,
    color: bool = True,
    dry_run: bool = False,
    encoding: str = "utf-8",
    version: bool = False,
) -> str:
    """
    Screenshot Helper for OSX Terminal

    Args:
        cmd: command, either cp or mv to copy or move. Default: cp
        src: source directory. If None provided, find using apple defaults. Default: None
        dst: destination directory. Default: .
        s: start at sth latest file. Default: 1
        n: number of files to copy/move: Default: 1
        color: toggle color output. Default: True
        dry_run: if True show an equivalent command that would be run. Default: False
        encoding: encoding to use for shell. Default: utf-8
        version: if True show version, else run shot. Default: False
    """
    if version:
        return __version__

    err_msg = ""
    accepted_cmds = ["cp", "mv"]
    if cmd not in accepted_cmds:
        err_msg += f"cmd must be in {accepted_cmds}. got:{cmd}\n"

    if src:
        src = os.path.expanduser(src)
        if not os.path.isdir(src):
            err_msg += f"src must be a directory. got:{src}\n"

    dst = os.path.expanduser(dst)
    if not os.path.isdir(dst):
        err_msg += f"dst must be a directory. got:{dst}\n"

    if n < 1:
        err_msg += f"n must be > 0. got:{n}\n"
    if s < 1:
        err_msg += f"s must be > 0. got:{s}\n"

    if err_msg:
        if color:
            err_msg = colored(err_msg, "red")

        return err_msg

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
        err_msg = f"No files found in {screenshot_dir_parsed}"
        if color:
            err_msg = colored(err_msg, "red")
        return err_msg

    if len(screenshots_to_copy) < n:
        warning_msg = f"Warning: there are not enough files to copy with s:{s}, n:{n}"
        if color:
            warning_msg = colored(warning_msg, "yellow")
        print(warning_msg)

    equivalent_command = " ".join([cmd, " ".join(screenshots_to_copy), dst])
    if dry_run:
        return equivalent_command

    success_msg = (
        f"{commands[cmd]} the following files to {dst} successfully!\n{screenshots_to_copy}"
    )
    err_msg = f"{equivalent_command} failed"
    if color:
        success_msg = colored(success_msg, "green")
        err_msg = colored(err_msg, "red")

    try:
        for screenshot_to_copy in screenshots_to_copy:
            if cmd == "cp":
                shutil.copy(screenshot_to_copy, dst)
            elif cmd == "mv":
                shutil.move(screenshot_to_copy, dst)
        return success_msg
    except Exception as e:
        return err_msg


if __name__ == "__main__":
    fire.Fire(shot)
