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


def _get_shell_output(args: List[str], encoding: str) -> str:
    # subprocess stdout is in bytes with trailing new line. need to decode and strip to get string back.
    # e.g. b'700aa82a2b0c\n' -> '700aa82a2b0c'
    return subprocess.check_output(args).decode(encoding).strip()


def _confirm() -> bool:
    return Prompt.ask("Do you want to continue?", choices=["y", "n"]) == "y"


# TODO: refactor to class?
# TODO: test _confirm_extension
def _confirm_extension(src: str, dst: str) -> bool:
    if os.path.isdir(dst):
        return True

    src_ext, dst_ext = map(lambda x: os.path.splitext(x)[1], [src, dst])
    if src_ext == dst_ext:
        return True

    print(
        termcolor.colored(
            f"src and dst extensions don't match. src: {src_ext}, dst: {dst_ext}", "yellow"
        )
    )
    return _confirm()


def _validate_args(src: str, dst: str, num: int, start: int) -> str:
    err_msg = ""
    if src:
        src = os.path.expanduser(src)
        if not os.path.isdir(src):
            err_msg += f"src must be a directory. got:{src}\n"
    dst = os.path.expanduser(dst)
    # TODO: add when num > 1 to warning
    if num > 1 and not os.path.isdir(dst):
        err_msg += f"dst must be a directory. got:{dst}\n"
    if start < 1:
        err_msg += f"start must be > 0. got:{start}\n"
    if num < 1:
        err_msg += f"num must be > 0. got:{num}\n"
    return err_msg


def _validate_screenshots_to_copy(
    screenshots_to_copy: List[str],
    screenshot_dir_parsed: str,
    start: int,
    num: int,
    yes: bool
):
    if len(screenshots_to_copy) < 1:
        return termcolor.colored(f"No files found in {screenshot_dir_parsed}", "red")
    if len(screenshots_to_copy) < num:
        print(
            termcolor.colored(
                f"Warning: there are not enough files to copy with start:{start}, num:{num}",
                "yellow",
            )
        )
        if not yes and not _confirm():
            return True
    return False


def shot(
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
    if version:
        return __version__

    if not color:
        termcolor.colored = lambda message, color: message  # type: ignore

    cmd = "mv" if mv else "cp"
    err_msg = _validate_args(src, dst, num, start)
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
    screenshots_to_copy = all_screenshots[start - 1 : start + num - 1]
    screenshot_err = _validate_screenshots_to_copy(
        screenshots_to_copy,
        screenshot_dir_parsed,
        start,
        num,
        yes
    )
    if screenshot_err:
        return screenshot_err

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
            if not _confirm_extension(screenshot_to_copy, dst):
                return
            if cmd == "cp":
                shutil.copy(screenshot_to_copy, dst)
            elif cmd == "mv":
                shutil.move(screenshot_to_copy, dst)
            # no need for else, should be handled above by `if cmd not in accepted_cmds:`
        if not quiet:
            return success_msg
    except Exception as e:
        print(err_msg)
        if debug:
            raise e
        raise SystemExit(1)


def main():
    fire.Fire(shot)


if __name__ == "__main__":
    main()
