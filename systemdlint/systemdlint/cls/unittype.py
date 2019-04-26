import copy
from systemdlint.cls.helper import Helper
from systemdlint.conf.knownPaths import KNOWN_DROPIN_PATHS

def GetDropinPaths(unit, runargs):
    res = []
    for k,v in KNOWN_DROPIN_PATHS.items():
        if unit.endswith(k):
            res = copy.deepcopy(v)
            res = [Helper.GetPath(runargs.rootpath, x.replace("%unit%", unit)) for x in res]
    return res