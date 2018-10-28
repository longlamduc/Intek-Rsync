#!/usr/bin/env python3
import argparse
import os
from os import path

# def load_file():
def copy_file(source, dest):
    file = os.open(source, os.O_RDONLY)
    file_copy = os.open(dest, os.O_RDWR | os.O_CREAT)
    content = os.read(file, 16 * 1024)
    os.write(file_copy, content)
    time = os.stat(file)
    atime = time.st_atime
    mtime = time.st_mtime
    os.utime(path.abspath(dest), (atime, mtime))
    os.chmod(path.abspath(dest), time.st_mode)
    os.close(file)
    os.close(file_copy)





parser = argparse.ArgumentParser()
parser.add_argument("src", action = "store", help = "source file")
parser.add_argument("dest", action = "store", help = "destination file")
args = parser.parse_args()
source  = args.src
dest = args.dest
strpath = path.abspath(dest)

if path.isfile(path.abspath(source)):
    copy_file(source, dest)
