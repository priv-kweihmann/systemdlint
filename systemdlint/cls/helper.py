import os
import re
import subprocess


class Helper(object):

    @staticmethod
    def GetPath(*args):
        _res = ["/"]
        for i in args:
            if i.startswith("/"):
                _res.append(i[1:])
            else:
                _res.append(i)
        return os.path.join(*_res)

    @staticmethod
    def StripLeftAll(_in, needles):
        while any([_in.startswith(x) for x in needles]):
            for k in needles:
                if _in.startswith(k):
                    _in = _in.lstrip(k)
        return _in

    @staticmethod
    def GetSystemdVersion(rootpath, default):
        try:
            out = subprocess.check_output(
                ["strings", "-n", "12", Helper.GetPath(rootpath, "/lib/systemd/systemd")], universal_newlines=True)
            for m in re.finditer(r"systemd\s(?P<version>\d\d\d)", out, re.MULTILINE):
                try:
                    val = int(m.group("version")) / 100.0
                    return str(val)
                except Exception:
                    pass
            return default
        except subprocess.CalledProcessError:
            return default
