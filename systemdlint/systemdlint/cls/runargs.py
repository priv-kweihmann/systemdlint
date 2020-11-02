import argparse
import os
import sys

from systemdlint.cls.helper import Helper

RUNARGS = None

DEFAULT_VERSION = "9.99999"


def __isNoDropIn(_file):
    name, ext = os.path.splitext(os.path.basename(_file))
    parentdir = os.path.basename(os.path.dirname(_file))
    if ext == ".conf" and parentdir.endswith(".d"):
        return False
    return True


def ArgParser():
    global RUNARGS
    global DEFAULT_VERSION
    parser = argparse.ArgumentParser(
        prog="systemdlint", description='Systemd Unitfile Linter')
    parser.add_argument("--nodropins", default=False,
                        action="store_true", help="Ignore Drop-Ins for parsing")
    parser.add_argument("--rootpath", default="/", help="Root path")
    parser.add_argument("--sversion", default=DEFAULT_VERSION,
                        help="Version of Systemd to be used")
    parser.add_argument("--output", default=sys.stderr,
                        help="Where to flush the findings (default: stderr)")
    parser.add_argument("--norootfs", action="store_true", default=False,
                        help="Run only unit file related tests")
    parser.add_argument("--gentests", default=False,
                        action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("files", nargs='+', help="Files to parse")
    RUNARGS = parser.parse_args()
    # Turn all paths to abs-paths right here
    RUNARGS.files = [os.path.abspath(x)
                     for x in RUNARGS.files if __isNoDropIn(x)]
    if RUNARGS.sversion == DEFAULT_VERSION:
        # Auto determine used systemd version, if not overriden from outside
        RUNARGS.sversion = Helper.GetSystemdVersion(
            RUNARGS.rootpath, DEFAULT_VERSION)
    return RUNARGS
