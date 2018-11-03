#!/usr/bin/env python3
import argparse
import os
from os import path


def get_arguments():    # get all the arguments from terminal
    parser = argparse.ArgumentParser()
    parser.add_argument("src", action="store", help="source file")
    parser.add_argument("dest", action="store", help="destination file")
    parser.add_argument("-u", "--update", action="store_true",
                        help="skip files that are newer on the receiver")
    parser.add_argument("-c", "--checksum", action="store_true",
                        help="skip based on checksum, not mod-time & size")
    args = parser.parse_args()
    return args


def checktime(src_path, dest_path):
    src_status = os.stat(src_path)
    dest_status = os.stat(dest_path)
    smtime = src_status.st_mtime
    dmtime = dest_status.st_mtime
    if dmtime > smtime:
        return False
    return True


def checksum(src_path, dest_path):
    if not path.exists(dest_path):
        return False
    else:
        file = os.open(src_path, os.O_RDONLY)
        dest_file = os.open(dest_path, os.O_RDONLY)
        src_content = os.read(file, path.getsize(src_path))
        dest_content = os.read(dest_file, path.getsize(dest_path))
        for x in range(len(src_content)):
            if src_content[x] != dest_content[x]:
                return False
        return True


def change_time_permission(src_path, dest_path):
    # update time and permission of destination file
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
    status = os.stat(file)
    content = os.read(file, status.st_size)
    os.write(file_copy, content)
    os.close(file)
    os.close(file_copy)


def update(src_path, dest_path):
    file = os.open(src_path, os.O_RDONLY)
    src_content = os.read(file, path.getsize(src_path))
    dest_file = os.open(dest_path, os.O_RDWR | os.O_CREAT)
    dest_content = os.read(dest_file, path.getsize(dest_path))
    count = 0
    while count < path.getsize(src_path):
        os.lseek(file, count, 0)
        os.lseek(dest_file, count, 0)
        if count < len(dest_content):
            if dest_content[count] != src_content[count]:
                os.write(dest_file, os.read(file, 1))
        else:
            os.write(dest_file, os.read(file, 1))
        count += 1


def link(src_path, dest_path):
    if os.stat(src_path).st_nlink > 1:
        os.unlink(dest_path)
        os.link(src_path, dest_path)
    elif os.path.islink(src_path):
        sym_link = os.readlink(src_path)
        os.unlink(dest_path)
        os.symlink(sym_link, dest_path)


def check(src_path, dest_path):
    src_status = os.stat(src_path)
    dest_status = os.stat(dest_path)
    smtime = src_status.st_mtime  # mtime and size of source
    ssize = src_status.st_size
    dmtime = dest_status.st_mtime  # mtime and size of dest
    dsize = dest_status.st_size
    if smtime == dmtime and ssize == dsize:
        return True
    return False


def main():
    args = get_arguments()
    source = args.src
    dest = args.dest
    change = 1
    rsync = 0
    # get source path and dest path
    src_path = path.abspath(source)
    # rsync
    if not path.exists(src_path):       # source doesn't exist
        print('rsync: link_stat "' + src_path +
              '" failed: No such file or directory (2)')
    elif not os.access(src_path, os.R_OK):  # cannot read source
        print('rsync: send_files failed to open "' + src_path +
              '": Permission denied (13)')
    elif path.isdir(src_path):            # source is directory
        print('skipping directory', source)
    else:
        if path.isdir(path.abspath(dest)):
            t = source.split('/')
            dest_path = path.abspath(dest) + '/' + t[len(t) - 1]
        else:
            dest_path = path.abspath(dest)
        if args.checksum:
            # if -c is chosen
            if checksum(src_path, dest_path):
                change = 0
        elif args.update:
            # if -u argument is chosen
            if not checktime(src_path, dest_path):
                # check if dest file is newer than src file or not
                change = 0
                # if dest_path is newer then no change happen
        if change == 1 and src_path != dest_path:
            # rsync will be executed
            if not path.exists(dest_path):
                file = os.open(dest_path, os.O_CREAT)
                copy_file(src_path, dest_path)
                rsync = 1
            else:
                if not check(src_path, dest_path):
                    rsync = 1
                    if path.getsize(src_path) < path.getsize(dest_path):
                        copy_file(src_path, dest_path)
                    else:
                        update(src_path, dest_path)
            if rsync == 1:
                change_time_permission(src_path, dest_path)
                link(src_path, dest_path)


main()
