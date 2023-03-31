import os
import re
import subprocess
from typing import List, Callable
import importlib
import inspect
import glob


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

    @staticmethod
    def GetSubClasses(module_obj: object, cls_type_cb: Callable, fn_pattern: str = "*") -> List[object]:
        res = []
        base_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..'))
        current_dir = os.path.dirname(inspect.getfile(module_obj.__class__))
        for file in glob.glob(current_dir + "/" + fn_pattern):
            name, _ = os.path.splitext(file)
            package_path = os.path.relpath(name, base_path).replace('/', '.')

            # Ignore __ files
            if name.startswith("__"):
                continue
            module = importlib.import_module(package_path)

            for m in inspect.getmembers(module, inspect.isclass):
                inst = cls_type_cb(module_obj, m[1])
                if inst:
                    res.append(inst)
        return res
