# Standard Library
import os
import shutil
import unittest

# Third party
import pytest

# shot
from shot import Shot


def setup_dirs(tmp_path, nfiles=1):
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"

    src_dir.mkdir()
    dst_dir.mkdir()

    for i in range(1, nfiles + 1):
        last_src_file = src_dir / f"foo{i}.txt"
        last_src_file.write_text(f"foo{i}")

    return src_dir, dst_dir, last_src_file


def tear_down_dirs(tmp_path):
    shutil.rmtree(tmp_path)


def test_cp(tmp_path):
    """
    src file should be unchanged, dst file should exist after running shot
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    expected_output_path = dst_dir / "foo1.txt"
    assert os.path.exists(src_file) == True
    assert os.path.exists(expected_output_path) == False
    Shot(src=str(src_dir), dst=str(dst_dir))()
    assert os.path.exists(src_file) == True
    assert os.path.exists(expected_output_path) == True
    tear_down_dirs(tmp_path)


def test_mv(tmp_path):
    """
    src file should not exist after running shot, dst file should
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    expected_output_path = dst_dir / "foo1.txt"
    assert os.path.exists(src_file) == True
    assert os.path.exists(expected_output_path) == False
    Shot(src=str(src_dir), dst=str(dst_dir), mv=True)()
    assert os.path.exists(src_file) == False
    assert os.path.exists(expected_output_path) == True


def test_cp_to_file(tmp_path):
    """
    dst dir exists but dst/bar.txt does not.
    shot should create it by copying src/foo1.txt to dst/bar.txt
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    expected_output_path = dst_dir / "bar.txt"
    assert os.path.exists(src_file) == True
    assert os.path.exists(expected_output_path) == False
    s = Shot(src=str(src_dir), dst=str(expected_output_path))
    s._confirm = lambda: True  # avoid capturing stdin during test
    s()
    assert os.path.exists(src_file) == True
    assert os.path.exists(expected_output_path) == True


def test_mv_to_file(tmp_path):
    """
    dst dir exists but dst/bar.txt does not.
    shot should create it by copying src/foo1.txt to dst/bar.txt
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    expected_output_path = dst_dir / "bar.txt"
    assert os.path.exists(src_file) == True
    assert os.path.exists(expected_output_path) == False
    Shot(src=str(src_dir), dst=str(expected_output_path), mv=True)()
    assert os.path.exists(src_file) == False
    assert os.path.exists(expected_output_path) == True


def test_cp_multiple(tmp_path):
    src_dir, dst_dir, src_file = setup_dirs(tmp_path, nfiles=2)
    expected_output_path_one = dst_dir / "foo1.txt"
    expected_output_path_two = dst_dir / "foo2.txt"
    assert os.path.exists(expected_output_path_one) == False
    assert os.path.exists(expected_output_path_two) == False
    Shot(src=str(src_dir), dst=str(dst_dir), num=2)()
    assert os.path.exists(expected_output_path_one) == True
    assert os.path.exists(expected_output_path_two) == True


# error handling
def test_cp_file_exists(tmp_path):
    """
    should fail because src and dst are the same.
    print error and systemexist.
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    with pytest.raises(SystemExit) as context:
        s = Shot(src=str(src_dir), dst=str(src_dir))
        s._confirm = lambda: True  # avoid capturing stdin during test
        s()
    assert (1,) == context.value.args


def test_debug_cp_file_exists(tmp_path):
    """
    should fail because src and dst are the same.
    latest file will be foo, will fail to copy since it already exists.
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    with pytest.raises(Exception) as context:
        s = Shot(src=str(src_dir), dst=str(src_dir), debug=True)
        s._confirm = lambda: True  # avoid capturing stdin during test
        s()
    assert f"'{src_file}' and '{src_file}' are the same file" in context.value.args


def test_debug_mv_file_exists(tmp_path):
    """
    should fail because src and dst are the same.
    latest file will be foo, will fail to copy since it already exists.
    """
    src_dir, dst_dir, src_file = setup_dirs(tmp_path)
    with pytest.raises(Exception) as context:
        s = Shot(src=str(src_dir), dst=str(src_dir), mv=True, debug=True)
        s._confirm = lambda: True  # avoid capturing stdin during test
        s()
    assert f"Destination path '{src_file}' already exists" in context.value.args
