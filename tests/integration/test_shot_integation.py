# Standard Library
import os
import unittest

# Third party
import pytest

# shot
from shot import shot


def setup_dirs(tmp_path):
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"

    src_dir.mkdir()
    dst_dir.mkdir()

    src_file = src_dir / "foo.txt"
    src_file.write_text("foo")
    return src_dir, dst_dir, src_file


def test_cp(tmp_path):
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    expected_output_path = dst_dir / "foo.txt"

    assert os.path.exists(expected_output_path) == False
    shot(src=str(src_dir), dst=str(dst_dir))
    assert os.path.exists(expected_output_path) == True


def test_cp_file_exists(tmp_path):
    """
    should fail because src and dst are the same.
    print error and systemexist.
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    with pytest.raises(SystemExit) as context:
        shot(src=str(src_dir), dst=str(src_dir))

    assert (1,) == context.value.args


def test_debug_cp_file_exists(tmp_path):
    """
    should fail because src and dst are the same.
    latest file will be foo, will fail to copy since it already exists.
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    with pytest.raises(Exception) as context:
        shot(src=str(src_dir), dst=str(src_dir), debug=True)

    assert f"'{src_file}' and '{src_file}' are the same file" in context.value.args


def test_debug_mv_file_exists(tmp_path):
    """
    should fail because src and dst are the same.
    latest file will be foo, will fail to copy since it already exists.
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    with pytest.raises(Exception) as context:
        shot(src=str(src_dir), dst=str(src_dir), mv=True, debug=True)

    assert f"Destination path '{src_file}' already exists" in context.value.args


def test_cp_to_file(tmp_path):
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    expected_output_path = dst_dir / "bar.txt"

    assert os.path.exists(expected_output_path) == False
    shot(src=str(src_dir), dst=str(expected_output_path))
    assert os.path.exists(expected_output_path) == True
