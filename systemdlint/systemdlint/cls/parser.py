
from systemdlint.cls.unititem import UnitItem
from SystemdUnitParser import SystemdUnitParser
from systemdlint.cls.unittype import GetDropinPaths
from systemdlint.cls.error import *
from systemdlint.conf.knownMandatory import KNOWN_MANDATORY
from systemdlint.conf.knownUnits import KNOWN_UNITS_MUST_HAVE_UNITSECTION, KNOWN_UNITS_EXT
from configparser import MissingSectionHeaderError, ParsingError
import glob
import os

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
                    return lines.index(l)
        return -1

    def __parseFile(self, file, runargs):
        res = []
        __x = SystemdUnitParser()
        if not os.path.isfile(file):
            return res
        with open(file) as i:
            try:
                __x.read_file(i)
            except (MissingSectionHeaderError, ParsingError) as e:
                _file, fileext = os.path.splitext(file)
                if fileext in KNOWN_UNITS_EXT:
                    msg = e.message.split("\n")[0]
                    res.append(UnitItem(file=file, line=e.lineno, preerror=[ErrorSyntaxError(msg, 1, file)]))
                else:
                    return res
            except UnicodeDecodeError:
                ## This seems to be a binary
                return res

        for section in dict(__x).keys():
            for k,v in dict(__x[section]).items():
                if isinstance(v, tuple) or isinstance(v, list):
                    for i in v:
                        res.append(UnitItem(file=file, line=self.__getLineFromFile(file, [k, "=", i]), section=section, key=k, value=i))
                else:
                    res.append(UnitItem(file=file, line=self.__getLineFromFile(file, [k, "=", v]), section=section, key=k, value=v))
        
        _file, fileext = os.path.splitext(file)
        _filemode = os.stat(file).st_mode
        _filemodeExpected = [0o100644, 0o100660, 0o100664, 0o100640]
        if not "Unit" in dict(__x).keys() and fileext in KNOWN_UNITS_MUST_HAVE_UNITSECTION:
            res.append(UnitItem(file=file, preerror=[ErrorUnitSectionMissing(file)]))
        if fileext and fileext not in KNOWN_UNITS_EXT:
            res.append(UnitItem(file=file, preerror=[ErrorUnknownUnitType(fileext, file)]))
        if not _filemode in _filemodeExpected:
            res.append(UnitItem(file=file, preerror=[ErrorFileMaskWrong(_filemode, _filemodeExpected, file)]))

        if not runargs.nodropins:
            for p in GetDropinPaths(os.path.basename(file), runargs):
                for f in glob.glob(p):
                    d_res = self.__parseFile(f)
                    for item in d_res:
                        # for r_key in [x for x in res if x.Section == item.Section and x.Key == item.Key]:
                        #     res.remove(r_key)
                        res.append(item)

        for k,v in KNOWN_MANDATORY.items():
            if k in dict(__x).keys():
                for opt in v:
                    if not any([x for x in res if x.Section == k and x.Key == opt]):
                        res.append(UnitItem(file=file, preerror=[ErrorMandatoryOptionMissing(opt, k, file)]))
        return list(set(res))

    def GetResults(self):
        return list(set(self.__unititems))
