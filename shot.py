# Standard Library
import os
import subprocess
from glob import glob
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


# TODO: change dry_run default to False
# add enum for cmd, either cp or mv
def shot(
    cmd: str = "cp",
    src: str = None,
    dest: str = ".",
    s: int = 1,
    n: int = 1,
    dry_run: bool = True,
    encoding: str = "utf-8",
    version: bool = False,
) -> str:
    """
    Screenshot Helper for OSX Terminal

    Args:
        cmd: command, either cp or mv. Default: cp
        src: source directory. If None provided, find using apple defaults. Default: None
        dest: destination directory. Default: .
        s: start at sth latest file. Default: 1
        n: number of files to copy/move: Default: 1
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
            err_msg += f"src: {src} is not a directory\n"

    dest = os.path.expanduser(dest)
    if not os.path.isdir(dest):
        err_msg += f"dest: {dest} is not a directory\n"

    if n < 1:
        err_msg += f"n: {n} < 1"
    if s < 1:
        err_msg += f"s: {s} < 1"

    if err_msg:
        return colored(err_msg, "red")
        # print(colored(err_msg, "red"))
        # raise ArgumentError(err_msg)

    if src:
        screenshot_dir = src
    else:
        screenshot_dir = _get_shell_output(
            "defaults read com.apple.screencapture location".split(), encoding
        )

    screenshot_dir_parsed = os.path.expanduser(screenshot_dir)
    all_screenshots = sorted(glob(f"{screenshot_dir_parsed}/*"), key=os.path.getctime, reverse=True)
    screenshots_to_copy = all_screenshots[s - 1 : s + n - 1]
    if len(screenshots_to_copy) < n:
        print(colored(f"Warning: there are not enough files to copy with s:{s}, n:{n}", "yellow"))

    # latest_file = max(all_screenshots, key=os.path.getctime)

    command = f"{cmd} {' '.join(screenshots_to_copy)} {dest}"
    if dry_run:
        return command

    subprocess.run(command.split())
    return colored(f"{commands[cmd]} {screenshots_to_copy} to {dest} successfully!")


if __name__ == "__main__":
    fire.Fire(shot)
