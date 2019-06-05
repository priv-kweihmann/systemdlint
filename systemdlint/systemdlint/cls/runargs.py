import argparse
import sys
import os
from systemdlint.cls.helper import Helper

RUNARGS = None

DEFAULT_VERSION = "9.99999"

def ArgParser():
    global RUNARGS
    global DEFAULT_VERSION
    parser = argparse.ArgumentParser(prog="systemdlint", description='Systemd Unitfile Linter')
    parser.add_argument("--nodropins", default=False, action="store_true", help="Ignore Drop-Ins for parsing")
    parser.add_argument("--rootpath", default="/", help="Root path")
    parser.add_argument("--sversion", default=DEFAULT_VERSION, help="Version of Systemd to be used")
    parser.add_argument("--output", default=sys.stderr, help="Where to flush the findings (default: stderr)")
    parser.add_argument("files", nargs='+', help="Files to parse")
    RUNARGS = parser.parse_args()
    ## Turn all paths to abs-paths right here
    RUNARGS.files = [os.path.abspath(x) for x in RUNARGS.files]
    if RUNARGS.sversion == DEFAULT_VERSION:
        ## Auto determine used systemd version, if not overriden from outside
        RUNARGS.sversion = Helper.GetSystemdVersion(RUNARGS.rootpath, DEFAULT_VERSION)
    return RUNARGS