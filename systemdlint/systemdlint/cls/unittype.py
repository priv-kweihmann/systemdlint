import copy
from systemdlint.cls.helper import Helper

__DROPIN_PATHS = {
    "user.conf": [
        "/etc/systemd/%unit%.d/*.conf", "/run/systemd/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf"
    ],
    "system.conf": [
        "/etc/systemd/%unit%.d/*.conf", "/run/systemd/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf"
    ],
    ".service": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".target": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".mount": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".automount": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".device": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".swap": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".path": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".timer": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".scope": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
    ".slice": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/system/%unit%.d/*.conf"
    ],
}

def GetDropinPaths(unit, runargs):
    global __DROPIN_PATHS
    res = []
    for k,v in __DROPIN_PATHS.items():
        if unit.endswith(k):
            res = copy.deepcopy(v)
            res = [Helper.GetPath(runargs.rootpath, x.replace("%unit%", unit)) for x in res]
    return res