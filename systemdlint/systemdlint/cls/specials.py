from systemdlint.cls.error import *
from systemdlint.cls.unititem import UnitItem
import re
from anytree import Node, LoopError, TreeError

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

class SpecialForwardReverseOption(object):
    def Run(self, stash):
        uniqunits = list(set([x.UnitName for x in stash]))
        check_items = [
                        ["Before", "After"],
                        ["Requires", "RequiredBy"],
                        ["Wants", "WantedBy"],
                        ["PropagatesReloadTo", "ReloadPropagatedFrom"],
                        ["ReloadPropagatedFrom", "PropagatesReloadTo"]
                        ]
        for u in uniqunits:
            for c in check_items:
                _na = [x for x in stash if x.Key == c[0] and x.UnitName == u]
                _nb = [x for x in stash if x.Key == c[1] and x.UnitName == u]
                _l = list(set([x.Value for x in _na]) & set([x.Value for x in _nb]))
                for l in _l:
                    _ia = next(obj for obj in _na if obj.Value == l)
                    _ib = next(obj for obj in _nb if obj.Value == l)
                    stash.append(UnitItem(file=_ia.File, line=_ia.Line, preerror=[
                            ErrorConflictingOptions("'{}' and '{}' cannot be set to the same value of '{}'".format(c[0], c[1], l), _ia.Line, _ia.File)
                        ]))
                    stash.append(UnitItem(file=_ib.File, line=_ib.Line, preerror=[
                            ErrorConflictingOptions("'{}' and '{}' cannot be set to the same value of '{}'".format(c[0], c[1], l), _ib.Line, _ib.File)
                        ]))
        return stash

class SpecialRestartAlwaysConflicts(object):
    def Run(self, stash):
        restart_always = [x for x in stash if x.Key == "Restart" and x.Value == "always"]
        for r in restart_always:
            conflicts = [x for x in stash if x.Key == "Conflicts" and x.Value == r.UnitName]
            for c in conflicts:
                stash.append(UnitItem(file=c.File, line=c.Line, 
                        preerror=[ErrorConflictingOptions("Conflicts={} does not terminate the unit, because it has set Restart=always".format(c.Value), c.Line, c.File)]))
        return stash

class SpecialDepCycle(object):
    def __getNodeFromException(self, msg):
        m = re.match(r"^.*Node\(\'(?P<path>.*)\'\)\.$", msg)
        if m:
            return [x for x in m.group("path").split("/") if x]
        return []

    def __buildTree(self, stash):
        _nodes = []
        for x in [x for x in stash if x.Key in ["After"]]:
            _n = None
            _m = None
            try:
                _t = [y for y in _nodes if y.name == x.Value]
                if not any(_t):
                    _n = Node(x.Value)
                    _nodes.append(_n)
                else:
                    _n = _t[0]
                _t = [y for y in _nodes if y.name == x.UnitName]
                if not any(_t):
                    _m = Node(x.UnitName)
                    _nodes.append(_m)
                else:
                    _m = _t[0]
                if not _m in _n.children:
                    _n.children += (_m,)
            except LoopError as e:
                _path = self.__getNodeFromException(str(e)) + [x.UnitName]
                stash.append(UnitItem(file=x.File, line=x.Line, preerror=[ErrorCyclicDependency(_path, x.Line, x.File)]))
        for x in [x for x in stash if x.Key in ["Before"]]:
            try:
                _n = None
                _t = [y for y in _nodes if y.name == x.UnitName]
                if not any(_t):
                    _n = Node(x.UnitName)
                    _nodes.append(_n)
                else:
                    _n = _t[0]
                _t = [y for y in _nodes if y.name == x.Value]
                _m = None
                if not any(_t):
                    _m = Node(x.Value)
                    _nodes.append(_m)
                else:
                    _m = _t[0]
                if not _m in _n.children:
                    _n.children += (_m,)
            except LoopError as e:
                _path = [x.UnitName] + self.__getNodeFromException(str(e))
                stash.append(UnitItem(file=x.File, line=x.Line, preerror=[ErrorCyclicDependency(_path, x.Line, x.File)]))
        return stash

    def Run(self, stash):
        return self.__buildTree(stash)

SPECIALS_SINGLEITEM = [
    SpecialTypeOneShotExecStart(),
    SpecialForwardReverseOption()
]

SPECIALS_ALLITEMS = [
    SpecialRestartAlwaysConflicts(),
    SpecialDepCycle(),
]