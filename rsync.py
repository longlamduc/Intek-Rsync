#!/usr/bin/env python3
import argparse
import os
from os import path
def get_file():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", action = "store", help = "source file")
    parser.add_argument("dest", action = "store", help = "destination file")
    args = parser.parse_args()
    return [args.src, args.dest]


def change_time_permission(source, dest):
    file = os.open(source, os.O_RDONLY)
    time = os.stat(file)
    atime = time.st_atime
    mtime = time.st_mtime
    os.utime(path.abspath(dest), (atime, mtime))
    os.chmod(path.abspath(dest), time.st_mode)
    os.close(file)


def copy_file(source, dest):
    file = os.open(source, os.O_RDONLY)
    if path.isdir(path.abspath(dest)):
        file_copy = os.open(path.abspath(dest)+'/'+source, os.O_RDWR | os.O_CREAT)
    else:
        file_copy = os.open(dest, os.O_RDWR | os.O_CREAT)
    content = os.read(file, 16 * 1024)
    os.write(file_copy, content)
    os.close(file)
    os.close(file_copy)


def link(source, dest):
    src_path = path.abspath(source)
    if path.isdir(path.abspath(dest)):
        dest_path = path.abspath(dest) + '/' + source
    else:
        dest_path = path.abspath(dest)
    if os.stat(src_path).st_nlink > 1:
        os.unlink(dest_path)
        os.link(src_path, dest_path)
    elif os.path.islink(src_path):
        sym_link = os.read_link(src_path)
        os.unlink(dest_path)
        os.symlink(sym_link, dest_path)


def main():
    tmp = get_file()
    source = tmp[0]
    dest  =tmp[1]
    strpath = path.abspath(dest)
    src_path = path.abspath(source)
    if path.isdir(src_path):
        print('skipping directory', source)
    elif path.isfile(src_path):
        copy_file(source, dest)
        change_time_permission(source, dest)
        link(source, dest)


main()
