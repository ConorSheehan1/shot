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


def test_copy(tmp_path):
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    expected_output_path = dst_dir / "foo.txt"

    assert os.path.exists(expected_output_path) == False
    shot(src=str(src_dir), dst=str(dst_dir))
    assert os.path.exists(expected_output_path) == True


def test_debug_cp_file_exists(tmp_path):
    """
    should fail because src and dest are the same.
    latest file will be foo, will fail to copy since it already exists.
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    with pytest.raises(Exception) as context:
        shot(src=str(src_dir), dst=str(src_dir), debug=True)

    assert f"'{src_file}' and '{src_file}' are the same file" in context.value.args


def test_debug_mv_file_exists(tmp_path):
    """
    should fail because src and dest are the same.
    latest file will be foo, will fail to copy since it already exists.
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    with pytest.raises(Exception) as context:
        shot(src=str(src_dir), dst=str(src_dir), mv=True, debug=True)

    assert f"Destination path '{src_file}' already exists" in context.value.args
