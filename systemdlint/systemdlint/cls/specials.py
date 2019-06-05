from systemdlint.cls.error import *
from systemdlint.cls.unititem import UnitItem

class SpecialTypeOneShotExecStart(object):
    def Run(self, stash):
        uniqunits = list(set([x.UnitName for x in stash]))
        for u in uniqunits:
            execstarts = [x for x in stash if x.Section == "Service" and x.Key == "ExecStart" and x.UnitName == u ]
            servtype = [x for x in stash if x.Section == "Service" and x.Key == "Type" and x.UnitName == u ]
            oneshots = [x for x in servtype if x.Value == "oneshot"]
            if any(oneshots):
                if not any(execstarts):
                    for i in oneshots:
                        stash.append(UnitItem(file=i.File, line=i.Line, preerror=[ErrorMultiplicity("oneshot services require at least one ExecStart", i.Line, i.File)]))
            else:
                if len(execstarts) > 1:
                    for i in execstarts[1:]:
                        stash.append(UnitItem(file=i.File, line=i.Line, preerror=[ErrorMultiplicity("This type of unit can only have 1 ExecStart setting", i.Line, i.File)]))
        return stash

class SpecialRestartAlwaysConflicts(object):
    def Run(self, stash):
        restart_always = [x for x in stash if x.Key == "Restart" and x.Value == "always"]
        for r in restart_always:
            conflicts = [x for x in stash if x.Key == "Conflicts" and x.Value == r.UnitName]
            for c in conflicts:
                stash.append(UnitItem(file=c.File, line=c.Line, 
                        preerror=[ErrorConflictingOptions("Conflicts={} does not terminate the unit, because it has set Restart=always", c.Line, c.File)]))
        return stash

SPECIALS_SINGLEITEM = [
    SpecialTypeOneShotExecStart()
]

SPECIALS_ALLITEMS = [
    SpecialRestartAlwaysConflicts(),
]