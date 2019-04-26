import datetime
import glob
import importlib
import ipaddress
import os
import pathlib
import re
import stat
import string
import sys

from urllib.parse import urlparse

from systemdlint.cls.error import *
from systemdlint.cls.helper import Helper
from systemdlint.conf.knownPaths import KNOWN_PATHS
from systemdlint.conf.knownUnits import KNOWN_UNITS_EXT

class Value(object):
    def __init__(self, conditional={}):
        self.__conditionals = conditional

    def CleanValue(self, value):
        _template = { 
            "%b": "123456",
            "%C": "/tmp",
            "%E": "/tmp",
            "%f": "foofile",
            "%h": "/tmp",
            "%H": "foohost",
            "%i": "fooinst",
            "%I": "fooinst",
            "%j": "foo",
            "%J": "foo",
            "%L": "/tmp",
            "%m": "foomachine",
            "%n": "foounit",
            "%N": "foounit",
            "%p": "foo",
            "%P": "foo",
            "%s": "/bin/sh",
            "%S": "/tmp",
            "%t": "/",
            "%T": "/tmp",
            "%g": "foogroup",
            "%G": "foogroup",
            "%u": "foouser",
            "%U": "foouser",
            "%v": "1.2.3",
            "%V": "/tmp",
            "%": "%"
        }
        for k, v in _template.items():
            value = value.replace(k, v)
        return Helper.StripLeftAll(value, self.__conditionals.keys())

    def IsAllowedValue(self, value):
        return False
    
    def AdditionalErrors(self, value, item, runargs):
        res = []
        if not self.__conditionals.keys():
            return res
        cond = value.replace(self.CleanValue(value), "")
        for k, v in self.__conditionals.items():
            if k in cond and v:
                module = importlib.import_module("systemdlint.cls.error")
                class_ = getattr(module, v)
                res.append(class_(item.Line, item.File))
        return list(set(res))

class NumericValue(Value):
    def __init__(self, lower=0, upper=9999999999999, base=1, suffixes=[], specials=[], conditional={}):
        self.__boundaries = [lower, upper]
        self.__suffixes = suffixes
        self.__specials = specials
        self.__base = base
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        val = self.CleanValue(value)
        while any([val.endswith(x) for x in self.__suffixes if x]):
            for x in self.__suffixes:
                val = val.rstrip(x)
        val = val.lstrip("-")
        return (str.isnumeric(val) and \
               int(val) >= self.__boundaries[0] and \
               int(val) <= self.__boundaries[-1]) or (val in self.__specials)

    def AdditionalErrors(self, value, item, runargs):
        res = []
        try:
            x = int(val)
            if x % self.__base != 0:
                res.append(ErrorInvalidNumericBase(item.Key, self.__base, item.Line, item.File))
        except:
            pass
        return res

class TextValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return True

class IPValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        try:
            ipaddress.IPv4Interface(self.CleanValue(value))
        except:
            try:
                ipaddress.IPv4Address(self.CleanValue(value))
            except:
                return False
        return True

class IPorUrlValue(Value):
    def __init__(self, conditional={}):
        self.__ipvalue = IPValue(conditional=conditional)
        self.__urlvalue = UrlListValue(conditional=conditional)
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return self.__ipvalue.IsAllowedValue(value) | \
               self.__urlvalue.IsAllowedValue(value)

class DeviceNodeValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return self.CleanValue(value).startswith("/dev/")

class TimeValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        _kv = { 
                "days" : "d",
                "day" : "d",
                "d" : "d",
                "hours" : "h",
                "hour" : "h",
                "hr" : "h",
                "h" : "h",
                "minutes": "min",
                "minute": "min",
                "min" : "min", 
                "M": "mon",
                "m" : "min",
                "month": "mon",
                "months": "mon", 
                "msec": "ms",
                "ms": "ms",
                "seconds": "s",
                "second": "s",
                "sec": "s",
                "s": "s",
                "usec": "us",
                "us": "us",
                "weeks": "w",
                "week": "w",
                "w": "w",
                "years": "y", 
                "year": "y",
                "y": "y",
                "µs": "us"
              }
        val = self.CleanValue(value)
        if not val.isnumeric():
            for m in re.finditer("^((?P<val>\d+)\s*(?P<mul>\w+)\s*)+".format("|".join(_kv.keys())), val):
                val = val.replace(m.group(0), "")
                try:
                    mul = _kv[m.group("mul")]
                    if int(m.group("val")) < 0:
                        raise Exception("Only pos values")
                    if mul == "us":
                        datetime.timedelta(microseconds=int(m.group("val")))
                    if mul == "ms":
                        datetime.timedelta(milliseconds=int(m.group("val")))
                    if mul == "s":
                        datetime.timedelta(seconds=int(m.group("val")))
                    if mul == "min":
                        datetime.timedelta(minutes=int(m.group("val")))
                    if mul == "h":
                        datetime.timedelta(hours=int(m.group("val")))
                    if mul == "d":
                        datetime.timedelta(days=int(m.group("val")))
                    if mul == "w":
                        datetime.timedelta(weeks=int(m.group("val")))
                    if mul == "mon":
                        datetime.timedelta(days=int(m.group("val")) * 30.44)
                    if mul == "y":
                        datetime.timedelta(days=int(m.group("val")) * 365.25)
                except Exception as e:
                    print(e)
                    return False
            if val:
                ## There is something left in the string
                return False
        return True

class BooleanValue(Value):
    def __init__(self, additionalKeyWords = [], conditional={}):
        self.__add = additionalKeyWords
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return self.CleanValue(value) in (["yes", "no", "true", "false", "0", "1", "on", "off"] + self.__add)

class PathValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        try:
            pathlib.Path(self.CleanValue(value))
            return True
        except:
            return False

class UsersValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return re.match(r"^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$", self.CleanValue(value))

class GroupsValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return re.match(r"^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$", self.CleanValue(value))

class EnumListValue(Value):
    def __init__(self, values, conditional={}):
        self.__values = values
        super().__init__(conditional)
    
    def IsAllowedValue(self, value):
        return all([self.CleanValue(x) in self.__values for x in value.split(" ") if x])

class EnumValue(EnumListValue):
    def __init__(self, value, conditional={}):
        super().__init__(value, conditional)

class SignalValue(EnumListValue):
    def __init__(self, conditional={}):
        signals = [str(x) for x in range(0, 60)]
        signals +=  ["SIGHUP", "SIGINT", "SIGQUIT", "SIGILL", "SIGABRT", "SIGFPE", \
                    "SIGKILL", "SIGSEGV", "SIGPIPE", "SIGALRM", "SIGTERM", "SIGUSR1", "SIGUSR2", \
                    "SIGCHLD", "SIGCONT", "SIGSTOP", "SIGTSTP", "SIGTTIN", "SIGTTOU", "SIGBUS", \
                    "SIGPOLL", "SIGPROF", "SIGSYS", "SIGTRAP", "SIGURG", "SIGVTALRM", "SIGXCPU", \
                    "SIGXFSZ", "SIGIOT", "SIGEMT", "SIGSTKFLT", "SIGIO", "SIGCLD", "SIGPWR", "SIGINFO", \
                    "SIGLOST", "SIGWINCH", "SIGUNUSED"]
        super().__init__(signals, conditional)

class OctalModeValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        try:
            int(self.CleanValue(value), 8)
            return True
        except:
            return False

class UrlListValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        res = True
        for item in self.CleanValue(value).split(" "):
            try:
                result = urlparse(val)
                if not result.scheme or not result.netloc:
                    raise Exception()
            except:
                res = False
                break
        return res

class UnitListValue(Value):
    def __init__(self, requiredExt="", conditional={}):
        self.__ext = requiredExt
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return all([x.endswith(self.__ext) for x in self.CleanValue(value).split(" ") if x])

    def AdditionalErrors(self, value, item, args):
        val = self.CleanValue(value)
        res = super().AdditionalErrors(value, item, args)
        for k in val.split(" "):
            found = False
            ## Skip unit with templates for now
            _file, fileext = os.path.splitext(k)
            if "@" in k or "%" in k or fileext not in KNOWN_UNITS_EXT:
                found = True
            else:
                for p in KNOWN_PATHS:
                    found = any([os.path.basename(x) == k for x in glob.glob(Helper.GetPath(args.rootpath, p))])
                    if found:
                        break
            if not found:
                res.append(ErrorRefUnitNotFound(k, item.Line, item.File))
        return list(set(res))

class AbsolutePathListValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return any([os.path.isabs(self.CleanValue(x)) for x in value.split(" ") if x])

class KeyValuePairListValue(Value):
    def __init__(self, delimiter="=", conditional={}):
        self.__delimiter = delimiter
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return any([self.__delimiter in x for x in value.split(" ") if x])

class ExecValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        if self.CleanValue(value):
            return True
        return False
    
    def AdditionalErrors(self, value, item, args):
        res = super().AdditionalErrors(value, item, args)
        com = self.CleanValue(value).split(" ")[0]
        if not os.path.exists(Helper.GetPath(args.rootpath, com)):
            res.append(ErrorExecNotFound(item.Line, item.File))
        else:
            _stat = os.stat(Helper.GetPath(args.rootpath, com))
            if (_stat.st_mode & stat.S_IXUSR) == 0:
                res.append(ErrorNoExecutable(item.Line, item.File))
        return list(set(res))

class CombinedValue(Value):
    def __init__(self, args, conditional={}):
        self.__args = args
        assert(all([issubclass(x.__class__, Value) for x in self.__args]))
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        res = True
        values = self.CleanValue(value).split(" ")
        for v in values:
            res &= self.__args[values.index(v)].IsAllowedValue(v)
        return res
    
    def AdditionalErrors(self, value, item, args):
        res = []
        values = self.CleanValue(value).split(" ")
        for v in values:
            res += self.__args[values.index(v)].AdditionalErrors(v, item, args)
        return list(set(res))
        
class EitherValue(Value):
    def __init__(self, args, conditional={}):
        self.__args = args
        assert(all([issubclass(x.__class__, Value) for x in self.__args]))
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        res = False
        for v in self.__args:
            res |= v.IsAllowedValue(self.CleanValue(value))
        return res

