from systemdlint.conf.knownSettings import KNOWN_SETTINGS
from systemdlint.cls.limitation import Limitation
from systemdlint.cls.error import *

class UnitItem(object):
    def __init__(self, file=None, line=None, section=None, key=None, value=None, preerror=[]):
        self.File = file
        self.Line = line
        self.Value = value
        self.Key = key
        self.Section = section
        self.__settingHandler = None
        self.__preerror = preerror

    def __repr__(self):
        return "{}{}{}{}{}".format(self.File, self.Line, self.Value, self.Key, self.Section)

    def __eq__(self, other):
        if isinstance(other, UnitItem):
            return str(other) == str(self)
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__repr__())
    
    def __getMatchingItem(self, sversion="9.99"):
        for item in KNOWN_SETTINGS:
            if item.Section == self.Section and \
               item.Name == self.Key:
               return item
        return None

    def Validate(self, runargs, stash):
        res = []
        if self.__preerror:
            ## In case we have pre-existing errors quit here
            return self.__preerror
        self.__settingHandler = self.__getMatchingItem(sversion=runargs.sversion)
        if not self.__settingHandler:
            res.append(ErrorInvalidSetting(self.Key, self.Section, self.Line, self.File))
        elif not self.__settingHandler.AllowedValue.IsAllowedValue(self.Value):
            res.append(ErrorInvalidValue(self.Key, self.Value, self.Line, self.File))
        else:
            res += self.__settingHandler.AllowedValue.AdditionalErrors(self.Value, self, runargs)
    
    
        if self.__settingHandler:
            ## Check on Restrictions
            if self.__settingHandler.Restricted:
                if self.__settingHandler.Restricted.Matches(stash, self):
                    res.append(ErrorSettingRestricted(self.Key, self.__settingHandler.Restricted, self.Line, self.File))

            ## Check on Required attributes
            if self.__settingHandler.Requires:
                if not self.__settingHandler.Requires.Matches(stash, self):
                    res.append(ErrorSettingRequires(self.Key, self.__settingHandler.Requires, self.Line, self.File))

            if float(self.__settingHandler.TillRel) <= float(runargs.sversion):
                res.append(ErrorDeprecated(self.Key, self.__settingHandler.TillRel, self.Line, self.File))
            if float(self.__settingHandler.SinceRel) >= float(runargs.sversion):
                res.append(ErrorTooNewOption(self.Key, self.__settingHandler.SinceRel, self.Line, self.File))
        return res
        