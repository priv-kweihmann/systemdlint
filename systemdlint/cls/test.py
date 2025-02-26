import os
import pathlib
from itertools import product

from systemdlint.cls.setting import Setting
from systemdlint.cls.value import NumericValue
from systemdlint.cls.value import UnitListValue
from systemdlint.conf.knownMandatory import KNOWN_MANDATORY
from systemdlint.conf.knownSettings import KNOWN_SETTINGS
from systemdlint.conf import knownUnits

class Test(object):
    def __init__(self, setting, prefix="Test", errorid="Foo", suffix="target", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setting = setting
        self.__prefix = prefix
        self.__errorid = errorid
        self.suffix = suffix

    def _findInKnownSettings(self, section, name):
        for i in KNOWN_SETTINGS:
            if i.Section == section and i.Name == name:
                return i
        return None

    def GetTestFileName(self, value, result, version=None):
        if not version:
            version = 2.31
            if float(self.setting.TillRel) < version:
                version = float(self.setting.TillRel)
            elif float(self.setting.SinceRel) > version:
                version = float(self.setting.SinceRel)
            version = "{:.2f}".format(version)
        classifier = "good"
        if result != 0:
            classifier = "bad"
        return "auto/{}/{}/{}/{}_{}_{}{}".format(
            self.__errorid,
            version,
            classifier,
            self.setting.Section,
            self.setting.Name,
            pathlib.urlquote_from_bytes(
                os.fsencode(str(value).replace("/", "--"))),
            self.suffix)

    def __GetMandatoryOptions(self):
        res = ["[Unit]", "Description=Foo"]
        if self.setting.Section in KNOWN_MANDATORY.keys():
            for x in KNOWN_MANDATORY[self.setting.Section]:
                y = self._findInKnownSettings(self.setting.Section, x)
                if y:
                    _unit = "[{}]".format(y.Section)
                    if _unit not in res:
                        res.append(_unit)
                    res.append("{}={}".format(
                        y.Name, y.AllowedValue.GetAllowedValues()[0]))
        return res

    def GetTestFileContent(self, value, prefix="auto", extra=[]):
        if isinstance(prefix, str):
            prefix = self.__GetMandatoryOptions()
        if value:
            res = "\n".join(prefix)
            if not "[{}]".format(self.setting.Section) in prefix:
                res += "\n[{}]".format(self.setting.Section)
            res += "\n{}={}".format(self.setting.Name, value)
            res += "\n"
            res += "\n".join(extra)
            res += "\n"
            return res
        else:
            res = "\n".join(prefix) + "\n"
            if extra:
                res += "\n".join(extra) + "\n"
            return res

    def GetTests(self):
        return []


class TestErrorDeprecated(Test):
    def __init__(self, setting, prefix='Test', errorid='OptionDeprecated', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        if self.setting.TillRel != "99.99":
            res.append((self.GetTestFileName(self.setting.AllowedValue.GetAllowedValues()[0], 0, version=self.setting.TillRel),
                        self.GetTestFileContent("123")))
            _newVersion = "{:.2f}".format(float(self.setting.TillRel) + 0.01)
            res.append((self.GetTestFileName(self.setting.AllowedValue.GetAllowedValues()[0], 1, version=_newVersion),
                        self.GetTestFileContent("123")))
        return res


class TestErrorTooNewOption(Test):
    def __init__(self, setting, prefix='Test', errorid='OptionTooNew', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        if self.setting.SinceRel != "0.0":
            res.append((self.GetTestFileName(self.setting.AllowedValue.GetAllowedValues()[0], 0, version=self.setting.SinceRel),
                        self.GetTestFileContent("123")))
            _newVersion = "{:.2f}".format(float(self.setting.SinceRel) - 0.01)
            res.append((self.GetTestFileName(self.setting.AllowedValue.GetAllowedValues()[0], 1, version=_newVersion),
                        self.GetTestFileContent("123")))
        return res


class TestErrorInvalidValue(Test):
    def __init__(self, setting, prefix='Test', errorid='InvalidValue', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        if isinstance(self.setting.AllowedValue, UnitListValue):
            # UnitListValue isn't support at the moment
            return res
        for x in self.setting.AllowedValue.GetAllowedValues():
            res.append((self.GetTestFileName(x, 0),
                        self.GetTestFileContent(x)))
        for x in self.setting.AllowedValue.GetInvalidValues():
            res.append((self.GetTestFileName(x, 1),
                        self.GetTestFileContent(x)))
        return res


class TestErrorInvalidNumericBase(Test):
    def __init__(self, setting, prefix='Test', errorid='InvalidNumericBase', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        if isinstance(self.setting.AllowedValue, NumericValue):
            if self.setting.AllowedValue.Base != 1:
                for x in self.setting.AllowedValue.GetAllowedValues(baseOnly=True):
                    res.append((self.GetTestFileName(x, 0),
                                self.GetTestFileContent(x)))
                for x in self.setting.AllowedValue.GetInvalidValues(baseOnly=True):
                    res.append((self.GetTestFileName(x, 1),
                                self.GetTestFileContent(x)))
        return res


class TestErrorUnknownUnitType(Test):
    def __init__(self, setting, prefix='Test', errorid='UnknownUnitType', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        for ext in knownUnits.KNOWN_UNITS_EXT:
            self.suffix = ext
            res.append((self.GetTestFileName("abc", 0),
                        self.GetTestFileContent("abc")))
            self.suffix = ext + "invalid"
            res.append((self.GetTestFileName("abc", 1),
                        self.GetTestFileContent("abc")))
        return res


class TestErrorSyntaxError(Test):
    def __init__(self, setting, prefix='Test', errorid='SyntaxError', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        res.append((self.GetTestFileName("abc", 1),
                    self.GetTestFileContent("", prefix=["aaa"])))
        res.append((self.GetTestFileName("abc2", 1),
                    self.GetTestFileContent("", prefix=["[Unit", "Foo==Bar"])))
        res.append((self.GetTestFileName("abc3", 1),
                    self.GetTestFileContent("", prefix=["Unit]", "Foo>Bar"])))
        return res


class TestErrorUnitSectionMissing(Test):
    def __init__(self, setting, prefix='Test', errorid='UnitSectionMissing', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        for ext in knownUnits.KNOWN_UNITS_MUST_HAVE_UNITSECTION:
            self.suffix = ext
            res.append((self.GetTestFileName("abc", 0),
                        self.GetTestFileContent("abc")))
            res.append((self.GetTestFileName("abc", 1),
                        self.GetTestFileContent("abc", prefix=[])))
        for ext in knownUnits.KNOWN_UNITS_EXT:
            if ext in knownUnits.KNOWN_UNITS_MUST_HAVE_UNITSECTION:
                continue
            self.suffix = ext
            res.append((self.GetTestFileName("abc", 0),
                        self.GetTestFileContent("abc", prefix=[])))
        return res


class TestErrorMandatoryOptionMissing(Test):
    def __init__(self, setting, prefix='Test', errorid='MandatoryOptionMissing', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        for k, v in KNOWN_MANDATORY.items():
            _prefix = ["[{}]".format(k)]
            _tmp = []
            for x in v:
                y = self._findInKnownSettings(k, x)
                if y:
                    _tmp.append("{}={}".format(
                        y.Name, y.AllowedValue.GetAllowedValues()[0]))
            self.setting = Setting("Mandatory", k)
            _unitprefix = ["[Unit]", "Description=Foo"]
            if k == "Unit":
                _unitprefix = []
            res.append((self.GetTestFileName(k, 0),
                        self.GetTestFileContent(None, prefix=_unitprefix, extra=_prefix + _tmp)))
            res.append((self.GetTestFileName(k, 1),
                        self.GetTestFileContent(None, prefix=_unitprefix, extra=_prefix)))
        return res


class TestErrorSettingRequires(Test):
    def __init__(self, setting, prefix='Test', errorid='SettingRequires', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        _res = {}
        i = 0
        for x in self.setting.Requires:
            _res[str(i)] = x.GetChunks()
            i += 1
        if _res.values():
            _product = list(product(*(_res.values())))
            for p in _product:
                _p = []
                for x in p:
                    _p += x
                _str = "-".join(_p)
                res.append((self.GetTestFileName(self.setting.AllowedValue.GetAllowedValues()[0] + _str, 0),
                            self.GetTestFileContent(self.setting.AllowedValue.GetAllowedValues()[0], extra=list(_p))))
                res.append((self.GetTestFileName(self.setting.AllowedValue.GetAllowedValues()[0] + _str, 1),
                            self.GetTestFileContent(self.setting.AllowedValue.GetAllowedValues()[0])))
        return res


class TestErrorSettingRestricted(Test):
    def __init__(self, setting, prefix='Test', errorid='SettingRestricted', suffix='.target', *args, **kwargs):
        super().__init__(setting, prefix=prefix,
                         errorid=errorid, suffix=suffix, *args, **kwargs)

    def GetTests(self):
        res = []
        _res = {}
        i = 0
        for x in self.setting.Restricted:
            _res[str(i)] = x.GetChunks()
            i += 1
        if _res.values():
            _product = list(product(*(_res.values())))
            for p in _product:
                _p = []
                for x in p:
                    _p += x
                _str = "-".join(_p)
                res.append((self.GetTestFileName(self.setting.AllowedValue.GetAllowedValues()[0] + _str, 1),
                            self.GetTestFileContent(self.setting.AllowedValue.GetAllowedValues()[0], extra=list(_p))))
                res.append((self.GetTestFileName(self.setting.AllowedValue.GetAllowedValues()[0] + _str, 0),
                            self.GetTestFileContent(self.setting.AllowedValue.GetAllowedValues()[0])))
        return res
