#!/usr/bin/env python3
# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("echo", help = "bla bla")
# args = parser.parse_args()
# print (args.echo)

import argparse

parser = argparse.ArgumentParser(description='Short sample app', add_help = True)

parser.add_argument('-a', action="store_true", default=False)
parser.add_argument('-b', action="append", dest="b")
parser.add_argument('-c', action="store", dest="cax", help = "ahihi",type=int)
a = parser.parse_args()
# print (parser.parse_args(['-a', '-bval', '-c', '3']))
print(a.b)
