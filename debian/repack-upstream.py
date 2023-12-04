#!/usr/bin/python3
import sys
import os
import tarfile
import tempfile

UPSTREAM_VERSION = sys.argv[2]
EXCLUDE_LIST = [
    "libffi",
    "libgomp",
    "libquadmath",
    "libssp",
    "libada",
    "libgfortran",
    "libcilkrts",
    "libgo",
    "libjava",
    "zlib",
    "gcc/testsuite/ada",
    "gcc/testsuite/gfortran",
    "gcc/testsuite/gnat",
    "gcc/testsuite/go.dg",
    "gcc/testsuite/go.go-torture",
    "gcc/testsuite/go.test",
    "gcc/testsuite/objc",
    "gcc/testsuite/obj-c++.dg",
    "gcc/testsuite/objc.dg",
    "gcc/testsuite/objc-obj-c++-shared",
    "gcc/ada/doc",
]
GCC_TMP_DIR = None


def get_orig_file_name():
    file_names_list = os.listdir('..')
    orig_files = []
    search_expresion = UPSTREAM_VERSION + '.orig'

    for file_name in file_names_list:
        if search_expresion in file_name:
            orig_files.append(file_name)

    if len(orig_files) != 1:
        raise ValueError('More than one file matched expresion {}.'.format(search_expresion))

    return '../' + orig_files[0]


def filter_function(tarinfo):
    for exclude in EXCLUDE_LIST:

        if exclude in tarinfo.name:
            return None
    tarinfo.name = os.path.relpath('/' + tarinfo.name, GCC_TMP_DIR)
    return tarinfo


def get_gcc_file(dir):
    for root, dirs, files in os.walk(tmpdir, topdown=False):
        for filename in files:
            if filename.startswith('gcc.tar'):
                return os.path.join(root, filename)
    raise Exception('gcc tarball not found')


def replace_all_texi_files(dir):
    for root, dirs, files in os.walk(dir, topdown=False):
        for filename in files:
            if filename.endswith('.texi'):
                path = os.path.join(root, filename)
                with open(path, 'w') as fh:
                    fh.write("Please refer to the gcc package documentation")


tarball_path = get_orig_file_name()

with tempfile.TemporaryDirectory() as tmpdir:
    with tarfile.open(tarball_path) as tar:
        tar.extractall(tmpdir)
    gcc_path = get_gcc_file(tmpdir)
    os.remove(tarball_path)

    with tempfile.TemporaryDirectory() as gcc_tmp_dir:
        with tarfile.open(gcc_path) as tar:
            tar.extractall(gcc_tmp_dir)

        replace_all_texi_files(gcc_tmp_dir)
        GCC_TMP_DIR = gcc_tmp_dir
        with tarfile.open(tarball_path, 'w:xz') as tarwriter:
            tarwriter.add(gcc_tmp_dir, filter=filter_function)
