import argparse
import sys
import os

RUNARGS = None

def ArgumentParser():
    global RUNARGS
    parser = argparse.ArgumentParser(prog="systemdlint", description='Systemd Unitfile Linter')
    parser.add_argument("--nodropins", default=False, action="store_true", help="Ignore Drop-Ins for parsing")
    parser.add_argument("--rootpath", default="/", help="Root path")
    parser.add_argument("--sversion", default="2.41", help="Version of Systemd to be used")
    parser.add_argument("--output", default=sys.stderr, help="Where to flush the findings (default: stderr)")
    parser.add_argument("files", nargs='+', help="Files to parse")
    RUNARGS = parser.parse_args()
    ## Turn all paths to abs-paths right here
    RUNARGS.files = [os.path.abspath(x) for x in RUNARGS.files]
    return RUNARGS