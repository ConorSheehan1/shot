# Standard Library
import glob
import os
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


# TODO: add enum for cmd, either cp or mv
def shot(
    cmd: str = "cp",
    src: str = None,
    dest: str = ".",
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
        cmd: command, either cp or mv recommended. Default: cp
        src: source directory. If None provided, find using apple defaults. Default: None
        dest: destination directory. Default: .
        s: start at sth latest file. Default: 1
        n: number of files to copy/move: Default: 1
        color: toggle color output. Default: True
        dry_run: if True show what command would be run. If False execute the command. Default: False
        encoding: encoding to use for shell. Default: utf-8
        version: if True show version, else run shot. Default: False
    """
    if version:
        return __version__

    err_msg = ""
    if src:
        src = os.path.expanduser(src)
        if not os.path.isdir(src):
            err_msg += f"src must be a directory. got:{src}\n"

    dest = os.path.expanduser(dest)
    if not os.path.isdir(dest):
        err_msg += f"dest must be a directory. got:{dest}\n"

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
            ["defaults", "read", "com.apple.screencapture location"], encoding
        )

    screenshot_dir_parsed = os.path.expanduser(screenshot_dir)

    # all files in screenshots dir, sorted from newest to oldest
    all_screenshots = sorted(
        glob.glob(f"{screenshot_dir_parsed}/*"), key=os.path.getctime, reverse=True
    )
    screenshots_to_copy = all_screenshots[s - 1 : s + n - 1]
    if len(screenshots_to_copy) < n:
        warning_msg = f"Warning: there are not enough files to copy with s:{s}, n:{n}"
        if color:
            warning_msg = colored(warning_msg, "yellow")
        print(warning_msg)

    command = f"{cmd} {' '.join(screenshots_to_copy)} {dest}"
    if dry_run:
        return command

    success_msg = f"{commands[cmd]} {screenshots_to_copy} to {dest} successfully!"
    if color:
        success_msg = colored(success_msg, "green")

    subprocess.run(command.split())
    return success_msg


if __name__ == "__main__":
    fire.Fire(shot)
