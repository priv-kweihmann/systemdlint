import datetime
import glob
import importlib
import ipaddress
import os
import pathlib
import re
import stat
import string
from itertools import product
from urllib.parse import urlparse

from systemdlint.cls.error import ErrorExecNotFound
from systemdlint.cls.error import ErrorInvalidNumericBase
from systemdlint.cls.error import ErrorInvalidValue
from systemdlint.cls.error import ErrorMountUnitNaming
from systemdlint.cls.error import ErrorNoExecutable
from systemdlint.cls.error import ErrorRefUnitNotFound
from systemdlint.cls.helper import Helper
from systemdlint.conf.knownPaths import KNOWN_PATHS
from systemdlint.conf.knownUnits import KNOWN_RUNTIME_UNITS
from systemdlint.conf.knownUnits import KNOWN_UNITS_EXT
from systemdlint.conf.knownUnits import KNOWN_GENERATED_UNITS


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

    def GetAllowedValues(self):
        return []

    def GetInvalidValues(self):
        return []


class NumericValue(Value):
    def __init__(self, lower=0, upper=9999999999999, base=1, suffixes=[], specials=[], conditional={}, numberBase=10):
        self.__boundaries = [lower, upper]
        self.__suffixes = suffixes
        self.__specials = specials
        self.Base = base
        self.__numberBase = numberBase
        super().__init__(conditional)

    def __getPlainValue(self, value):
        val = self.CleanValue(value)
        for x in self.__suffixes:
            val = val.rstrip(x)
        return val

    def IsAllowedValue(self, value):
        val = self.__getPlainValue(value)
        val2 = val.lstrip("-")
        charSet = string.digits
        if self.__numberBase == 16:
            charSet = string.hexdigits + "x"
        elif self.__numberBase == 8:
            charSet = string.octdigits
        if val2 in self.__specials:
            return True
        return (all(c in charSet for c in val2) and
                int(val, self.__numberBase) >= self.__boundaries[0] and
                int(val, self.__numberBase) <= self.__boundaries[-1])

    def AdditionalErrors(self, value, item, runargs):
        res = []
        try:
            val = self.__getPlainValue(value)
            if val in self.__specials:
                return res
            x = int(val, self.__numberBase)
            if x % self.Base != 0:
                res.append(ErrorInvalidNumericBase(
                    item.Key, self.Base, item.Line, item.File))
        except Exception as e:
            print(str(e))
        return res

    def GetAllowedValues(self, baseOnly=False):
        res = []
        _suffixess = self.__suffixes or [""]
        __lower = self.__boundaries[0]
        __upper = self.__boundaries[-1]
        if self.__numberBase == 16:
            __lower = hex(__lower)
            __upper = hex(__upper)
        if self.__numberBase == 8:
            __lower = oct(__lower)
            __upper = oct(__upper)
        if not baseOnly:
            for x in _suffixess:
                res.append("{}{}".format(__lower, x))
                res.append("{}{}".format(__upper, x))
            for x in self.__specials:
                res.append(x)
        else:
            if self.Base != 1:
                for i in range(self.Base, self.Base * 10, self.Base):
                    if self.__numberBase == 16:
                        res.append(hex(i))
                    if self.__numberBase == 8:
                        res.append(oct(i))
        return res

    def GetInvalidValues(self, baseOnly=False):
        res = []
        _suffixess = self.__suffixes or [""]
        __lower = self.__boundaries[0] - 1
        __upper = self.__boundaries[-1] + 1
        if self.__numberBase == 16:
            __lower = hex(__lower)
            __upper = hex(__upper)
        if self.__numberBase == 8:
            __lower = oct(__lower)
            __upper = oct(__upper)
        if not baseOnly:
            for x in _suffixess:
                res.append("{}{}".format(__lower, x))
                res.append("{}{}".format(__upper, x))
        else:
            if self.Base != 1:
                for i in range(self.Base, self.Base * 10, self.Base):
                    if self.__numberBase == 16:
                        res.append(hex(i + 1))
                    if self.__numberBase == 8:
                        res.append(oct(i + 1))
        return res


class HexValue(NumericValue):
    def __init__(self, lower=0, upper=9999999999999, base=1, suffixes=[], specials=[], conditional={}):
        super().__init__(lower=lower, upper=upper, base=base, suffixes=suffixes,
                         specials=specials, conditional=conditional, numberBase=16)
        self.__boundaries = [lower, upper]
        self.__suffixes = suffixes
        self.__specials = specials

    def GetAllowedValues(self, baseOnly=False):
        res = []
        _suffixess = self.__suffixes or [""]
        if not baseOnly:
            for x in _suffixess:
                res.append("{:02x}{}".format(self.__boundaries[0], x))
                res.append("{:02x}{}".format(self.__boundaries[-1], x))
            for x in self.__specials:
                res.append(x)
        else:
            if self.Base != 1:
                for i in range(self.Base, self.Base * 10, self.Base):
                    res.append("{:02x}".format(i))
        return res

    def GetInvalidValues(self, baseOnly=False):
        res = []
        _suffixess = self.__suffixes or [""]
        if not baseOnly:
            for x in _suffixess:
                res.append("{:02x}{}".format(self.__boundaries[0] - 1, x))
                res.append("{:02x}{}".format(self.__boundaries[-1] + 1, x))
        else:
            if self.Base != 1:
                for i in range(self.Base, self.Base * 10, self.Base):
                    res.append("{:02x}".format(i))
        return res


class TextValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return True

    def GetAllowedValues(self):
        return ["abc"]

    def GetInvalidValues(self):
        return []


class EmptyValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return not value

    def GetAllowedValues(self):
        return [""]

    def GetInvalidValues(self):
        return ["a"]

class ListOf(Value):
    def __init__(self, obj, delimiter=" ", conditional={}):
        super().__init__(conditional)
        self.__object = obj
        self.__delimiter = delimiter

    def IsAllowedValue(self, value):
        return all(self.__object.IsAllowedValue(x) for x in self.CleanValue(value).split(self.__delimiter) if x)

    def GetAllowedValues(self):
        if any(self.__object.GetAllowedValues()):
            return [self.__delimiter.join(self.__object.GetAllowedValues())]
        return []

    def GetInvalidValues(self):
        res = []
        if any(self.__object.GetInvalidValues()):
            res = [self.__delimiter.join([str(x) for x in self.__object.GetInvalidValues()])]
            if any(self.__object.GetAllowedValues()):
                _x = [str(x) for x in self.__object.GetAllowedValues()] + [str(self.__object.GetInvalidValues()[0])]
                res.append(self.__delimiter.join(_x))
        return res

class IPValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        try:
            ipaddress.IPv4Interface(self.CleanValue(value))
        except Exception:
            try:
                ipaddress.IPv4Address(self.CleanValue(value))
            except Exception:
                return False
        return True

    def GetAllowedValues(self):
        return [
            "1.1.1.1/0",
            "255.255.255.255/32",
            "1.1.1.1",
            "255.255.255.255"
        ]

    def GetInvalidValues(self):
        return [
            "1.1.1.1/-1",
            "255.255.255.255/33",
            "-1.1.1.1",
            "256.255.255.255",
            "abc",
            "255.255.255.256",
            "255.256.255.255",
            "0.0.0.",
            "0/abc"
        ]


class IPorUrlValue(Value):
    def __init__(self, conditional={}):
        self.__ipvalue = IPValue(conditional=conditional)
        self.__urlvalue = UrlListValue(conditional=conditional)
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return self.__ipvalue.IsAllowedValue(value) | \
            self.__urlvalue.IsAllowedValue(value)

    def GetAllowedValues(self):
        return self.__ipvalue.GetAllowedValues() + self.__urlvalue.GetAllowedValues()

    def GetInvalidValues(self):
        return self.__ipvalue.GetInvalidValues() + self.__urlvalue.GetInvalidValues()


class DeviceNodeValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return self.CleanValue(value).startswith("/dev/")

    def GetAllowedValues(self):
        return ["/dev/foo", "/dev/bar"]

    def GetInvalidValues(self):
        return ["/tmp", "/devvvv", "/tmp/dev", "dev/foo"]


class TimeValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)
        self._kv = {
            "days": "d",
            "day": "d",
            "d": "d",
            "hours": "h",
            "hour": "h",
            "hr": "h",
            "h": "h",
            "minutes": "min",
            "minute": "min",
            "min": "min",
            "M": "mon",
            "m": "min",
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

    def IsAllowedValue(self, value):
        val = self.CleanValue(value)
        if not val.isnumeric():
            if val == "infinity":
                # All time values should accept 'infinity'
                return True
            for m in re.finditer(r"^((?P<val>\d+)\s*(?P<mul>\w+)\s*)+".format("|".join(self._kv.keys())), val):
                val = val.replace(m.group(0), "")
                try:
                    mul = self._kv[m.group("mul")]
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
                # There is something left in the string
                return False
        return True

    def GetAllowedValues(self):
        i = 0
        res = []
        for k in self._kv.keys():
            res.append("{}{}".format(i, k))
            i += 1
        res += [
            "1years 2months 3days 4hours 5min 30usec",
            "infinity"
        ]
        return res

    def GetInvalidValues(self):
        return [True, "0.5d", "1p", "2potatoes", "3decades"]


class BooleanValue(Value):
    def __init__(self, additionalKeyWords=[], conditional={}):
        self.__add = additionalKeyWords
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return self.CleanValue(value) in (["yes", "no", "true", "false", "0", "1", "on", "off"] + self.__add)

    def GetAllowedValues(self):
        return ["yes", "no", "true", "false", "0", "1", "on", "off"] + self.__add

    def GetInvalidValues(self):
        return [x for x in ["bar", "foo", "baz"] if x not in self.__add]


class PathValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        try:
            pathlib.Path(self.CleanValue(value))
            return True
        except Exception:
            return False

    def GetAllowedValues(self):
        return ["/bin", "/usr/sbin"]

    def GetInvalidValues(self):
        return []


class UsersValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return re.match(r"^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$", self.CleanValue(value))

    def GetAllowedValues(self):
        return ["iamauser", "metoo"]

    def GetInvalidValues(self):
        return [1, 3, 4, True, "meisnotausercozofmyloooooooooooooooooooooooooooooooooognamegee"]


class GroupsValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return re.match(r"^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$", self.CleanValue(value))

    def GetAllowedValues(self):
        return ["iamagroup", "metoo"]

    def GetInvalidValues(self):
        return [1, 3, 4, True, "meisnotagroupcozofmyloooooooooooooooooooooooooooooooooognamegee"]


class EnumListValue(Value):
    def __init__(self, values, conditional={}):
        self.__values = values
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return all([self.CleanValue(x) in self.__values for x in value.split(" ") if x])

    def GetAllowedValues(self):
        return self.__values

    def GetInvalidValues(self):
        return []


class EnumValue(EnumListValue):
    def __init__(self, value, conditional={}):
        super().__init__(value, conditional)


class SignalValue(EnumListValue):
    def __init__(self, conditional={}):
        signals = [str(x) for x in range(0, 60)] + ["65"]
        signals += ["SIGHUP", "SIGINT", "SIGQUIT", "SIGILL", "SIGABRT", "SIGFPE",
                    "SIGKILL", "SIGSEGV", "SIGPIPE", "SIGALRM", "SIGTERM", "SIGUSR1", "SIGUSR2",
                    "SIGCHLD", "SIGCONT", "SIGSTOP", "SIGTSTP", "SIGTTIN", "SIGTTOU", "SIGBUS",
                    "SIGPOLL", "SIGPROF", "SIGSYS", "SIGTRAP", "SIGURG", "SIGVTALRM", "SIGXCPU",
                    "SIGXFSZ", "SIGIOT", "SIGEMT", "SIGSTKFLT", "SIGIO", "SIGCLD", "SIGPWR", "SIGINFO",
                    "SIGLOST", "SIGWINCH", "SIGUNUSED", "DATAERR"]
        super().__init__(signals, conditional)


class ErrorTypeValue(EnumListValue):
    def __init__(self, conditional={}):
        signals = ["E2BIG", "EACCES", "EADDRINUSE", "EADDRNOTAVAIL", "EAFNOSUPPORT", "EAGAIN", 
                   "EALREADY", "EBADE", "EBADF", "EBADFD", "EBADMSG", "EBADR", "EBADRQC", "EBADSLT", 
                   "EBUSY", "ECANCELED", "ECHILD", "ECHRNG", "ECOMM", "ECONNABORTED", "ECONNREFUSED", 
                   "ECONNRESET", "EDEADLK", "EDEADLOCK", "EDESTADDRREQ", "EDOM", "EDQUOT", "EEXIST", 
                   "EFAULT", "EFBIG", "EHOSTDOWN", "EHOSTUNREACH", "EHWPOISON", "EIDRM", "EILSEQ", 
                   "EINPROGRESS", "EINTR", "EINVAL", "EIO", "EISCONN", "EISDIR", "EISNAM", "EKEYEXPIRED", 
                   "EKEYREJECTED", "EKEYREVOKED", "EL2HLT", "EL2NSYNC", "EL3HLT", "EL3RST", "ELIBACC", 
                   "ELIBBAD", "ELIBEXEC", "ELIBMAX", "ELIBSCN", "ELNRANGE", "ELOOP", "EMEDIUMTYPE", 
                   "EMFILE", "EMLINK", "EMSGSIZE", "EMULTIHOP", "ENAMETOOLONG", "ENETDOWN", "ENETRESET", 
                   "ENETUNREACH", "ENFILE", "ENOANO", "ENOBUFS", "ENODATA", "ENODEV", "ENOENT", "ENOEXEC", 
                   "ENOKEY", "ENOLCK", "ENOLINK", "ENOMEDIUM", "ENOMEM", "ENOMSG", "ENONET", "ENOPKG", 
                   "ENOPROTOOPT", "ENOSPC", "ENOSR", "ENOSTR", "ENOSYS", "ENOTBLK", "ENOTCONN", "ENOTDIR", 
                   "ENOTEMPTY", "ENOTRECOVERABLE", "ENOTSOCK", "ENOTSUP", "ENOTTY", "ENOTUNIQ", "ENXIO", 
                   "EOPNOTSUPP", "EOVERFLOW", "EOWNERDEAD", "EPERM", "EPFNOSUPPORT", "EPIPE", "EPROTO", 
                   "EPROTONOSUPPORT", "EPROTOTYPE", "ERANGE", "EREMCHG", "EREMOTE", "EREMOTEIO", "ERESTART", 
                   "ERFKILL", "EROFS", "ESHUTDOWN", "ESOCKTNOSUPPORT", "ESPIPE", "ESRCH", "ESTALE", 
                   "ESTRPIPE", "ETIME", "ETIMEDOUT", "ETOOMANYREFS", "ETXTBSY", "EUCLEAN", "EUNATCH", 
                   "EUSERS", "EWOULDBLOCK", "EXDEV", "EXFULL"]
        super().__init__(signals, conditional)


class OctalModeValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        try:
            int(self.CleanValue(value), 8)
            return True
        except Exception:
            return False

    def GetAllowedValues(self):
        return ["002", "004", "006", "007", "777", "644"]

    def GetInvalidValues(self):
        return [True, "999", "888"]

class MacAddressValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        if any(re.match(x, self.CleanValue(value)) for x in [
                                r"([a-f0-9]{2}-){5}[a-f0-9]{2}",
                                r"([a-f0-9]{2}:){5}[a-f0-9]{2}",
                                r"([A-F0-9]{4}\.){2}[A-F0-9]{4}",
                                ]):
            return True
        return False

    def GetAllowedValues(self):
        return ["01:23:45:67:89:ab", "00-11-22-33-44-55", "AABB.CCDD.EEFF"]

    def GetInvalidValues(self):
        return [True, "01:23:45:67:89", "00-11-22-GG-44-55", "AABB:CCDD:EEFF"]


class UrlListValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        res = True
        for item in self.CleanValue(value).split(" "):
            try:
                result = urlparse(item)
                if not result.scheme and not result.netloc:
                    raise Exception()
            except Exception:
                res = False
                break
        return res

    def GetAllowedValues(self):
        return [
            "file://test.a.b.com",
            "http://a.b.com",
            "http://user:pwd@test.com:1234"
        ]

    def GetInvalidValues(self):
        return [
            1,
            True
        ]


class UnitListValue(Value):
    def __init__(self, requiredExt="", inverseMode=False, conditional={}):
        self.__ext = requiredExt
        self.__inverseMode = inverseMode
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return all([x.endswith(self.__ext) for x in self.CleanValue(value).split(" ") if x])

    def AdditionalErrors(self, value, item, args):
        val = self.CleanValue(value)
        res = super().AdditionalErrors(value, item, args)
        for k in val.split(" "):
            found = False
            # Skip unit with templates for now
            _file, fileext = os.path.splitext(k)
            if "@" in k or "%" in k or fileext not in KNOWN_UNITS_EXT:
                found = True
            elif fileext in KNOWN_RUNTIME_UNITS:
                # In case referenced unit is generated at runtime
                found = True
            else:
                for p in KNOWN_PATHS:
                    found = any([os.path.basename(x) == k for x in glob.glob(
                        Helper.GetPath(args.rootpath, p))])
                    if found:
                        break
            if any(re.match(x, k) for x in KNOWN_GENERATED_UNITS):
                # filter out known generated units
                # they are likely unavailable offline
                found = True
            if not found:
                res.append(ErrorRefUnitNotFound(k, item.Line, item.File))
        if self.__inverseMode:
            # Unit in Path must not reference other .path units
            _, ext = os.path.splitext(self.CleanValue(value))
            if ext == self.__ext:
                res.append(ErrorInvalidValue(
                    item.Key, value, item.Line, item.File))
        return list(set(res))

    def GetAllowedValues(self):
        return ["syslog.service"]

    def GetInvalidValues(self):
        return ["does_not_exist_in_any_case{}".format(x) for x in KNOWN_UNITS_EXT] + [1, True]


class AbsolutePathListValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return any([os.path.isabs(self.CleanValue(x)) for x in value.split(" ") if x])

    def GetAllowedValues(self):
        return ["/tmp", "/dev/"]

    def GetInvalidValues(self):
        return ["../../", "tmp", 1, True]


class MountPathValue(Value):
    def __init__(self, conditional={}):
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return os.path.isabs(self.CleanValue(value))

    def AdditionalErrors(self, value, item, args):
        res = []
        val = self.CleanValue(value).lstrip("/")
        name, ext = os.path.splitext(os.path.basename(item.File))
        name = name.lstrip("/")
        cname = name.replace("-", "/")
        if val != cname:
            res.append(ErrorMountUnitNaming(
                value.replace("-", "/"), item.File))
        return res

    def GetAllowedValues(self):
        return ["/tmp"]

    def GetInvalidValues(self):
        return [1, True, "this.isnt--gonna-work_here"]


class KeyValuePairListValue(Value):
    def __init__(self, delimiter="=", conditional={}):
        self.__delimiter = delimiter
        super().__init__(conditional)

    def IsAllowedValue(self, value):
        return any([self.__delimiter in x for x in value.split(" ") if x])

    def GetAllowedValues(self):
        return ["a{}b".format(self.__delimiter)]

    def GetInvalidValues(self):
        return ["a>b", 1, True]


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

    def GetAllowedValues(self):
        return ["/bin/sh"]

    def GetInvalidValues(self):
        return []


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

    def GetAllowedValues(self):
        res = []
        for x in self.__args:
            res.append(x.GetAllowedValues())
        _res = list(product(*res))
        return [" ".join(x) for x in _res]

    def GetInvalidValues(self):
        res = []
        for x in self.__args:
            res.append(x.GetInvalidValues())
        _res = list(product(*res))
        return [" ".join(x) for x in _res]


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

    def GetAllowedValues(self):
        res = []
        for x in self.__args:
            res += x.GetAllowedValues()
        return res

    def GetInvalidValues(self):
        # TODO - This is difficult to calculate for combi enum + text, as
        # it could be anything then
        return []
