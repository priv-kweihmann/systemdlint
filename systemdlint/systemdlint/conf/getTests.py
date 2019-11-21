import os
    
from systemdlint.cls.test import TestErrorDeprecated
from systemdlint.cls.test import TestErrorInvalidNumericBase
from systemdlint.cls.test import TestErrorInvalidValue
from systemdlint.cls.test import TestErrorMandatoryOptionMissing
from systemdlint.cls.test import TestErrorSettingRequires
from systemdlint.cls.test import TestErrorSettingRestricted
from systemdlint.cls.test import TestErrorSyntaxError
from systemdlint.cls.test import TestErrorTooNewOption
from systemdlint.cls.test import TestErrorUnitSectionMissing
from systemdlint.cls.test import TestErrorUnknownUnitType
from systemdlint.conf.knownSettings import KNOWN_SETTINGS

def getTests(outputPath):

    res = []
    for _s in KNOWN_SETTINGS:
        t = TestErrorDeprecated(_s)
        res += t.GetTests()
        t = TestErrorInvalidValue(_s)
        res += t.GetTests()
        t = TestErrorTooNewOption(_s)
        res += t.GetTests()
        t = TestErrorInvalidNumericBase(_s)
        res += t.GetTests()
        t = TestErrorSettingRequires(_s)
        res += t.GetTests()
        t = TestErrorSettingRestricted(_s)
        res += t.GetTests()
    # Now the parts that are setting unspecific
    t = TestErrorUnknownUnitType(KNOWN_SETTINGS[0])
    res += t.GetTests()
    t = TestErrorSyntaxError(KNOWN_SETTINGS[0])
    res += t.GetTests()
    t = TestErrorUnitSectionMissing(KNOWN_SETTINGS[0])
    res += t.GetTests()
    t = TestErrorMandatoryOptionMissing(None)
    res += t.GetTests()
    for s in res:
        try:
            _path = os.path.join(outputPath, s[0])
            os.makedirs(os.path.dirname(_path), exist_ok=True)
            with open(_path, "w") as o:
                o.write(s[1])
        except Exception:
            pass
