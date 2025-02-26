import argparse
import os
import sys
import re

from systemdlint.cls.helper import Helper
from systemdlint.cls.error import Error

RUNARGS = None

DEFAULT_VERSION = "9.99999"


def __isNoDropIn(_file):
    name, ext = os.path.splitext(os.path.basename(_file))
    parentdir = os.path.basename(os.path.dirname(_file))
    if ext == ".conf" and parentdir.endswith(".d"):
        return False
    return True


def __CheckMessageFormat(_messageformat: str):
    try:
        _messageformat.format(
            path="File",
            line="Line",
            severity="Severity",
            id="Msg",
            msg="Details")
    except KeyError as e:
        print(f"Argument --messageformat contains an unknown key: {e}\n"
              "Use one of: path, line, severity, id, msg.")
        exit(1)


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
    parser.add_argument('--messageformat', type=str, help='Format of message output')
    parser.add_argument("files", nargs='+', help="Files to parse")
    RUNARGS = parser.parse_args()
    # Turn all paths to abs-paths right here
    RUNARGS.files = [os.path.abspath(x)
                     for x in RUNARGS.files if __isNoDropIn(x)]
    if RUNARGS.sversion == DEFAULT_VERSION:
        # Auto determine used systemd version, if not overriden from outside
        RUNARGS.sversion = Helper.GetSystemdVersion(
            RUNARGS.rootpath, DEFAULT_VERSION)
    else:
        if not re.match(r'\d\.\d\d$', RUNARGS.sversion):
            raise ValueError('--sversion needs to be in the format of x.xx')
    if RUNARGS.messageformat is not None:
        __CheckMessageFormat(RUNARGS.messageformat)
        Error.MessageFormat = RUNARGS.messageformat
    return RUNARGS
