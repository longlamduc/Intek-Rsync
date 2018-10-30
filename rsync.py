#!/usr/bin/env python3
import argparse
import os
from os import path


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", action="store", help="source file")
    parser.add_argument("dest", action="store", help="destination file")
    parser.add_argument("-u", "--update", action="store_true",
                        help="skip files that are newer on the receiver")
    parser.add_argument("-c", "--checksum", action="store_true",
                        help="skip based on checksum, not mod-time & size")
    args = parser.parse_args()
    return args


def change_time_permission(src_path, dest_path):
    file = os.open(src_path, os.O_RDONLY)
    time = os.stat(file)
    atime = time.st_atime
    mtime = time.st_mtime
    os.utime(dest_path, (atime, mtime))
    os.chmod(dest_path, time.st_mode)
    os.close(file)


def copy_file(src_path, dest_path):
    file = os.open(src_path, os.O_RDONLY)
    file_copy = os.open(dest_path, os.O_RDWR)
    content = os.read(file, 16 * 1024)
    os.write(file_copy, content)
    os.close(file)
    os.close(file_copy)


def link(src_path, dest_path):
    if os.stat(src_path).st_nlink > 1:
        os.unlink(dest_path)
        os.link(src_path, dest_path)
    elif os.path.islink(src_path):
        sym_link = os.read_link(src_path)
        os.unlink(dest_path)
        os.symlink(sym_link, dest_path)


def check(src_path, dest_path):
    src_status = os.stat(src_path)
    dest_status = os.stat(dest_path)
    satime = src_status.st_atime #get atime, mtime and size of source
    smtime = src_status.st_mtime
    ssize = src_status.st_size
    datime = dest_status.st_atime #get atime, mtime and size of dest
    dmtime = dest_status.st_mtime
    dsize = dest_status.st_size
    if (satime, smtime, ssize) == (datime, dmtime, dsize):
        return True
    return False


def main():
    tmp = get_arguments()
    source = tmp.src
    dest = tmp.dest
    #get source path and dest path
    if path.isdir(path.abspath(dest)):
        dest_path = path.abspath(dest) + '/' + source
    else:
        dest_path = path.abspath(dest)
    src_path = path.abspath(source)
    #rsync
    if not path.exists(src_path):       #source doesn't exist
        print('rsync: link_stat "' + src_path +
                    '" failed: No such file or directory (2)')
    if path.isdir(src_path):            #source is dir
        print('skipping directory', source)
    elif path.isfile(src_path):         #source is file
        if not path.exists(dest_path):
            file = os.open(dest_path, os.O_CREAT)
            os.close(file)
        if not check(src_path, dest_path):
            copy_file(src_path, dest_path)
            change_time_permission(src_path, dest_path)
            link(src_path, dest_path)


main()
