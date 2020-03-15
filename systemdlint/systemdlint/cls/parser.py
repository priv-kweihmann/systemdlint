
import glob
import os
from configparser import MissingSectionHeaderError
from configparser import ParsingError

from systemdlint.cls.error import ErrorFileMaskWrong
from systemdlint.cls.error import ErrorMandatoryOptionMissing
from systemdlint.cls.error import ErrorSyntaxError
from systemdlint.cls.error import ErrorUnitSectionMissing
from systemdlint.cls.error import ErrorUnknownUnitType
from systemdlint.cls.specials import SPECIALS_ALLITEMS
from systemdlint.cls.specials import SPECIALS_SINGLEITEM
from systemdlint.cls.unititem import UnitItem
from systemdlint.cls.unittype import GetDropinPaths
from systemdlint.conf.knownMandatory import KNOWN_MANDATORY
from systemdlint.conf.knownUnits import KNOWN_UNITS_EXT
from systemdlint.conf.knownUnits import KNOWN_UNITS_MUST_HAVE_UNITSECTION
from SystemdUnitParser import SystemdUnitParser


class Parser(object):

    def __init__(self, runargs, files):
        self.__runargs = runargs
        self.__unititems = []
        for f in files:
            self.__unititems += self.__parseFile(f, runargs)

    def __getLineFromFile(self, file, needles):
        with open(file) as i:
            lines = i.readlines()
            for l in lines:
                if not l:
                    continue
                if all([l.find(x) != -1 for x in needles]):
                    return lines.index(l) + 1
        return -1

    def __parseFile(self, file, runargs):
        res = []
        __x = SystemdUnitParser()
        if not os.path.isfile(file):
            return res
        with open(file) as i:
            try:
                __x.read_file(i)
            except (MissingSectionHeaderError) as e:
                _file, fileext = os.path.splitext(file)
                if fileext in KNOWN_UNITS_EXT:
                    msg = e.message.split("\n")[0]
                    res.append(UnitItem(file=file, line=e.lineno,
                                        preerror=[ErrorSyntaxError(msg, 1, file)]))
                else:
                    return res
            except (ParsingError) as e:
                _file, fileext = os.path.splitext(file)
                if fileext in KNOWN_UNITS_EXT:
                    msg = e.message.split("\n")[0]
                    res.append(UnitItem(file=file, line=1, preerror=[
                               ErrorSyntaxError(msg, 1, file)]))
                else:
                    return res
            except UnicodeDecodeError:
                # This seems to be a binary
                return res

        for section in dict(__x).keys():
            for k, v in dict(__x[section]).items():
                if isinstance(v, tuple) or isinstance(v, list):
                    for i in v:
                        res.append(UnitItem(file=file, line=self.__getLineFromFile(
                            file, [k, "=", i]), section=section, key=k, value=i))
                else:
                    res.append(UnitItem(file=file, line=self.__getLineFromFile(
                        file, [k, "=", v]), section=section, key=k, value=v))

        _file, fileext = os.path.splitext(file)
        _filemode = os.stat(file).st_mode
        _filemodeExpected = [0o100644, 0o100660, 0o100664, 0o100640]
        if "Unit" not in dict(__x).keys() and fileext in KNOWN_UNITS_MUST_HAVE_UNITSECTION:
            res.append(UnitItem(file=file, preerror=[
                       ErrorUnitSectionMissing(file)]))
        if fileext and fileext not in KNOWN_UNITS_EXT:
            res.append(UnitItem(file=file, preerror=[
                       ErrorUnknownUnitType(fileext, file)]))
        if _filemode not in _filemodeExpected:
            res.append(UnitItem(file=file, preerror=[
                       ErrorFileMaskWrong(_filemode, _filemodeExpected, file)]))

        if not runargs.nodropins:
            for p in GetDropinPaths(os.path.basename(file), runargs):
                for f in glob.glob(p):
                    d_res = self.__parseFile(f, runargs)
                    for item in d_res:
                        res = item.RunDropInProcessor(res, runargs)

        for k, v in KNOWN_MANDATORY.items():
            if k in dict(__x).keys():
                for opt in v:
                    if not any([x for x in res if x.Section == k and x.Key == opt]):
                        res.append(UnitItem(file=file, preerror=[
                                   ErrorMandatoryOptionMissing(opt, k, file)]))

        for k in SPECIALS_SINGLEITEM:
            # Catch all the special cases
            res = k.Run(res, self.__runargs)

        return list(set(res))

    def GlobalValidate(self):
        for s in SPECIALS_ALLITEMS:
            self.__unititems = s.Run(list(set(self.__unititems)), self.__runargs)

    def GetResults(self):
        self.GlobalValidate()
        return list(set(self.__unititems))
