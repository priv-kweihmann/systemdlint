import os
import re
import sys

from anytree import LoopError
from anytree import Node

from systemdlint.cls.error import ErrorConflictingOptions
from systemdlint.cls.error import ErrorCyclicDependency
from systemdlint.cls.error import ErrorMultiplicity
from systemdlint.cls.error import ErrorSecurity
from systemdlint.cls.unititem import UnitItem


class SpecialTypeOneShotExecStart(object):
    def Run(self, stash, runargs):
        uniqunits = list(set([x.UnitName for x in stash]))
        for u in uniqunits:
            execstarts = [x for x in stash if x.Section ==
                          "Service" and x.Key == "ExecStart" and x.UnitName == u]
            servtype = [x for x in stash if x.Section ==
                        "Service" and x.Key == "Type" and x.UnitName == u]
            oneshots = [x for x in servtype if x.Value == "oneshot"]
            if any(oneshots):
                if not any(execstarts):
                    for i in oneshots:
                        stash.append(UnitItem(file=i.File, line=i.Line, preerror=[ErrorMultiplicity(
                            "oneshot services require at least one ExecStart", i.Line, i.File)]))
            else:
                if len(execstarts) > 1:
                    for i in execstarts[1:]:
                        stash.append(UnitItem(file=i.File, line=i.Line, preerror=[ErrorMultiplicity(
                            "This type of unit can only have 1 ExecStart setting", i.Line, i.File)]))
        return stash


class SpecialForwardReverseOption(object):
    def Run(self, stash, runargs):
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
                _l = list(set([x.Value for x in _na]) &
                          set([x.Value for x in _nb]))
                for l in _l:
                    _ia = next(obj for obj in _na if obj.Value == l)
                    _ib = next(obj for obj in _nb if obj.Value == l)
                    stash.append(UnitItem(file=_ia.File, line=_ia.Line, preerror=[
                        ErrorConflictingOptions("'{}' and '{}' cannot be set to the same value of '{}'".format(
                            c[0], c[1], l), _ia.Line, _ia.File)
                    ]))
                    stash.append(UnitItem(file=_ib.File, line=_ib.Line, preerror=[
                        ErrorConflictingOptions("'{}' and '{}' cannot be set to the same value of '{}'".format(
                            c[0], c[1], l), _ib.Line, _ib.File)
                    ]))
        return stash


class SpecialRestartAlwaysConflicts(object):
    def Run(self, stash, runargs):
        restart_always = [x for x in stash if x.Key ==
                          "Restart" and x.Value == "always"]
        for r in restart_always:
            conflicts = [x for x in stash if x.Key ==
                         "Conflicts" and x.Value == r.UnitName]
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
                if _m not in _n.children:
                    _n.children += (_m,)
            except LoopError as e:
                _path = self.__getNodeFromException(str(e)) + [x.UnitName]
                stash.append(UnitItem(file=x.File, line=x.Line, preerror=[
                             ErrorCyclicDependency(_path, x.Line, x.File)]))
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
                if _m not in _n.children:
                    _n.children += (_m,)
            except LoopError as e:
                _path = [x.UnitName] + self.__getNodeFromException(str(e))
                stash.append(UnitItem(file=x.File, line=x.Line, preerror=[
                             ErrorCyclicDependency(_path, x.Line, x.File)]))
        return stash

    def Run(self, stash, runargs):
        return self.__buildTree(stash)


class SpecialSecurityAssessment(object):
    def __is_priv_user(self, stash):
        _dynuser = [x for x in stash if x.Key == "DynamicUser"]
        _user = [x for x in stash if x.Key == "User"]
        return any([x.Value in ["0", "root"] for x in _dynuser + _user]) or (not _dynuser and not _user)

    def __access_logical_sets(self, stash, key, badvalues, emptybad=False):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        # get effective set first
        _effcaps = set()
        for c in [x for x in stash if x.Key == key]:
            _notmode = c.Value.startswith("~")
            if not c.Value:
                _effcaps = set()
            for sc in c.Value.lstrip("~").split(" "):
                if sc:
                    if _notmode:
                        _effcaps.discard(sc)
                    else:
                        _effcaps.add(sc)

        for b in badvalues:
            if b in _effcaps:
                res.append(UnitItem(file=_file, line=1, preerror=[
                    ErrorSecurity("Service sets not-recommended {} in {}".format(
                        b, key), _file, key)
                ]))
        if not _effcaps and emptybad:
            res.append(UnitItem(file=_file, line=1, preerror=[
                ErrorSecurity(
                    "Service doesn't set recommended {}".format(key), _file, key)
            ]))
        return res

    def __access_user(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        # User
        _dynuser = [x for x in stash if x.Key == "DynamicUser"]
        _user = [x for x in stash if x.Key == "User"]
        if not _dynuser and not _user:
            res.append(UnitItem(file=_file, line=1, preerror=[
                ErrorSecurity(
                    "Neither User nor DynamicUser is set", _file, "NoUser")
            ]))
        for u in _dynuser + _user:
            if u.Value in ["0", "root"]:
                res.append(UnitItem(file=u.File, line=u.Line, preerror=[
                    ErrorSecurity("Service should not run under {}=root".format(
                        u.Key), u.File, "UserRoot", u.Line)
                ]))
            if u.Value in ["nobody"]:
                res.append(UnitItem(file=u.File, line=u.Line, preerror=[
                    ErrorSecurity("Service should not run under {}=nobody".format(
                        u.Key), u.File, "UserNobody", u.Line)
                ]))
        return res

    def __access_subgroups(self, stash):
        res = []
        if not stash:
            return res
        if self.__is_priv_user(stash):
            return res
        if not UnitItem(file="magicfoo", section="Service", key="SupplementaryGroups").IsValidInVersion(self.__version):
            return res
        for _x in [x for x in stash if x.Key == "SupplementaryGroups"]:
            res.append(UnitItem(file=_x.File, line=_x.Line, preerror=[
                ErrorSecurity("Service should not use {}".format(
                    _x.Key), _x.File, "SupplementaryGroups", _x.Line)
            ]))
        return res

    def __access_remove_ipc(self, stash):
        res = []
        if not stash:
            return res
        if self.__is_priv_user(stash):
            return res
        if not UnitItem(file="magicfoo", section="Service", key="RemoveIPC").IsValidInVersion(self.__version):
            return res
        for _x in [x for x in stash if x.Key == "RemoveIPC"]:
            if _x.Value not in ["yes", "on", "1", "true"]:
                res.append(UnitItem(file=_x.File, line=_x.Line, preerror=[
                    ErrorSecurity("Service should set activate {}".format(
                        _x.Key), _x.File, "RemoveIPC", _x.Line)
                ]))
        return res

    def __access_rootdir(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        if not UnitItem(file="magicfoo", section="Service", key="RootDirectory").IsValidInVersion(self.__version) and \
           not UnitItem(section="Service", key="RootImage").IsValidInVersion(self.__version):
            return res
        _root = [x for x in stash if x.Key ==
                 "RootDirectory" or x.Key == "RootImage"]
        if not _root or any([x.Value in ["", "/"] for x in _root]):
            res.append(UnitItem(file=_file, line=1, preerror=[
                ErrorSecurity(
                    "Service should set RootDirectory or RootImage to non-root value", _file, "RootDirectory")
            ]))
        return res

    def __access_protect_sys(self, stash):
        res = []
        if not stash:
            return res
        if not UnitItem(file="magicfoo", section="Service", key="ProtectSystem").IsValidInVersion(self.__version):
            return res
        _file = stash[0].File
        _items = [x for x in stash if x.Key == "ProtectSystem"]
        if not _items:
            res.append(UnitItem(file=_file, line=1, preerror=[
                ErrorSecurity("Service should set ProtectSystem",
                              _file, "ProtectSystemNA")
            ]))
        else:
            for x in _items:
                if x.Value != "strict":
                    res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                        ErrorSecurity("Service should set ProtectSystem=strict",
                                      x.File, "ProtectSystemNStrict", x.Line)
                    ]))
        return res

    def __access_protect_home(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        if not UnitItem(file="magicfoo", section="Service", key="ProtectHome").IsValidInVersion(self.__version):
            return res
        _items = [x for x in stash if x.Key == "ProtectHome"]
        if not _items:
            res.append(UnitItem(file=_file, line=1, preerror=[
                ErrorSecurity("Service should set ProtectHome",
                              _file, "ProtectHomeNA")
            ]))
        else:
            for x in _items:
                if x.Value not in ["yes", "true", "1", "on"]:
                    res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                        ErrorSecurity(
                            "Service should set ProtectHome=yes", x.File, "ProtectHomeOff", x.Line)
                    ]))
        return res

    def __access_notify_access(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        if not UnitItem(file="magicfoo", section="Service", key="NotifyAccess").IsValidInVersion(self.__version):
            return res
        _items = [x for x in stash if x.Key == "NotifyAccess"]
        for x in _items:
            if x.Value == "all":
                res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                    ErrorSecurity(
                        "Service should not set NotifyAccess=all", x.File, "NotifyAccess", x.Line)
                ]))
        return res

    def __access_keyring_mode(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        if not UnitItem(file="magicfoo", section="Service", key="KeyringMode").IsValidInVersion(self.__version):
            return res
        _items = [x for x in stash if x.Key == "KeyringMode"]
        if not _items:
            res.append(UnitItem(file=_file, line=1, preerror=[
                ErrorSecurity("Service should set KeyringMode",
                              _file, "KeyringModeNA")
            ]))
        else:
            for x in _items:
                if x.Value != "private":
                    res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                        ErrorSecurity(
                            "Service should set KeyringMode=private", x.File, "KeyringModeNPriv", x.Line)
                    ]))
        return res

    def __access_ip_deny(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        if not UnitItem(file="magicfoo", section="Service", key="IPAddressDeny").IsValidInVersion(self.__version):
            return res
        _items = [x for x in stash if x.Key == "IPAddressDeny"]
        if not _items:
            res.append(UnitItem(file=_file, line=1, preerror=[
                ErrorSecurity("Service should set IPAddressDeny",
                              _file, "IPAddressDenyNA")
            ]))
        # TODO eval further rules like localhost only a.s.o.
        return res

    def __access_device_policy(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        if not UnitItem(file="magicfoo", section="Service", key="DevicePolicy").IsValidInVersion(self.__version):
            return res
        _devpolicy = [x.Value in ["strict", "closed"]
                      for x in stash if x.Key == "DevicePolicy"]
        if not _devpolicy:
            res.append(UnitItem(file=_file, line=1, preerror=[
                ErrorSecurity(
                    "Service should set DevicePolicy to strict or closed", _file, "DevicePolicy")
            ]))
        return res

    def __access_favor_set_boolean(self, stash, keys):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        for k in keys:
            if not UnitItem(file="magicfoo", section="Service", key=k).IsValidInVersion(self.__version):
                continue
            if not any([x.Value in ["yes", "true", "1", "on"] for x in stash if x.Key == k]):
                res.append(UnitItem(file=_file, line="1", preerror=[
                    ErrorSecurity(
                        "Service should have {} being set".format(k), _file, k)
                ]))
        return res

    def __access_favor_unset_boolean(self, stash, keys):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        for k in keys:
            if not UnitItem(file="magicfoo", section="Service", key=k).IsValidInVersion(self.__version):
                continue
            for x in [x for x in stash if x.Key == k if x.Value]:
                res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                    ErrorSecurity(
                        "Service should not set {}".format(k), x.File, k, x.Line)
                ]))
        return res

    def __assess_sys_call_arch(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        if not UnitItem(file="magicfoo", section="Service", key="SystemCallArchitectures").IsValidInVersion(self.__version):
            return res
        _hits = [x for x in stash if x.Key == "SystemCallArchitectures"]
        if not _hits:
            res.append(UnitItem(file=_file, line="1", preerror=[
                ErrorSecurity(
                    "Service should have {} being set".format("SystemCallArchitectures"), _file, "SystemCallArchitecturesNA")
            ]))
        elif not any([x.Value == "native" for x in _hits]):
            res.append(UnitItem(file=_file, line="1", preerror=[
                ErrorSecurity(
                    "Service can call multiple ABIs according to {}".format(
                        "SystemCallArchitectures"), _file,
                    "SystemCallArchitecturesMult", severity="warning")
            ]))
        return res

    def __assess_umask(self, stash):
        res = []
        if not stash:
            return res
        _file = stash[0].File
        if not UnitItem(file="magicfoo", section="Service", key="UMask").IsValidInVersion(self.__version):
            return res
        for x in [x for x in stash if x.Key == "UMask"]:
            try:
                _val = x.Value
                if _val == "infinity":
                    _val = str(sys.maxsize)
                _mask = int(_val, 8)
                if (_mask & int("0002", 8)):
                    res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                        ErrorSecurity(
                            "Files created by service are world-writeable", x.File, "UMaskOW", x.Line)
                    ]))
                elif (_mask & int("0004", 8)):
                    res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                        ErrorSecurity(
                            "Files created by service are world-readbale", x.File, "UMaskOR", x.Line)
                    ]))
                elif (_mask & int("0020", 8)):
                    res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                        ErrorSecurity(
                            "Files created by service are group-writeable", x.File, "UMaskGW", x.Line, severity="warning")
                    ]))
                elif (_mask & int("0040", 8)):
                    res.append(UnitItem(file=x.File, line=x.Line, preerror=[
                        ErrorSecurity(
                            "Files created by service are group-readbale", x.File, "UMaskGR", x.Line, severity="info")
                    ]))
            except:
                pass
        return res
    
    def __is_matching_unit(self, item):
        _file, _ext = os.path.splitext(item.File)
        if _ext in [".service"]:
            return True
        if _ext in [".conf"]:
            return os.path.basename(os.path.dirname(_file)).endswith(".service.d")
        return False

    def Run(self, stash, runargs):
        self.__version = runargs.sversion
        uniqunits = list(set([x.UnitName for x in stash if self.__is_matching_unit(x)]))
        for u in uniqunits:
            _sub_stash = [x for x in stash if x.UnitName == u]
            # User
            stash += self.__access_user(_sub_stash)
            # SupplementaryGroups
            stash += self.__access_subgroups(_sub_stash)
            # Options that should be set
            stash += self.__access_favor_set_boolean(_sub_stash, ["Delegate", "LockPersonality", "MemoryDenyWriteExecute", "NoNewPrivileges",
                                                                  "PrivateDevices", "PrivateMounts", "PrivateNetwork", "PrivateTmp",
                                                                  "PrivateUsers", "ProtectClock", "ProtectControlGroups", "ProtectHostname",
                                                                  "ProtectKernelLogs", "ProtectKernelModules", "ProtectKernelTunables",
                                                                  "RestrictRealtime", "RestrictSUIDSGID"])
            # Capabilities
            stash += self.__access_logical_sets(_sub_stash, "CapabilityBoundingSet",
                                                            ["CAP_AUDIT_CONTROL", "CAP_AUDIT_READ", "CAP_AUDIT_WRITE", "CAP_BLOCK_SUSPEND",
                                                             "CAP_CHOWN", "CAP_DAC_OVERRIDE", "CAP_DAC_READ_SEARCH", "CAP_FOWNER",
                                                             "CAP_FSETID", "CAP_IPC_LOCK", "CAP_IPC_OWNER", "CAP_KILL", "CAP_LEASE",
                                                             "CAP_LINUX_IMMUTABLE", "CAP_MAC_ADMIN", "CAP_MAC_OVERRIDE", "CAP_MKNOD",
                                                             "CAP_NET_ADMIN", "CAP_NET_BIND_SERVICE", "CAP_NET_BROADCAST", "CAP_NET_RAW",
                                                             "CAP_RAWIO", "CAP_SETFCAP", "CAP_SETGID", "CAP_SETPCAP", "CAP_SETUID",
                                                             "CAP_SYS_ADMIN", "CAP_SYS_BOOT", "CAP_SYS_CHROOT", "CAP_SYS_MODULE",
                                                             "CAP_SYS_NICE", "CAP_SYS_PACCT", "CAP_SYS_PTRACE", "CAP_SYS_RESOURCE",
                                                             "CAP_SYS_TIME", "CAP_SYS_TTY_CONFIG", "CAP_SYSLOG", "CAP_WAKE_ALARM"])
            # RestrictAddressFamilies
            stash += self.__access_logical_sets(_sub_stash, "RestrictAddressFamilies",
                                                            ["AF_INET", "AF_INET6", "AF_NETLINK", "AF_PACKET", "AF_UNIX"])
            # RestrictNamespaces
            stash += self.__access_logical_sets(_sub_stash, "RestrictNamespaces",
                                                            ["CLONE_NEWCGROUP", "CLONE_NEWIPC", "CLONE_NEWNET", "CLONE_NEWNS",
                                                             "CLONE_NEWPID", "CLONE_NEWUSER", "CLONE_NEWUTS"])
            # SystemCallFilter
            stash += self.__access_logical_sets(_sub_stash, "SystemCallFilter",
                                                            ["@clock", "@cpu-emulation", "@debug", "@module", "@mount", "@obsolete",
                                                             "@privileged", "@raw-io", "@reboot", "@resources", "@swap"], True)
            # SystemCallArchitectures
            stash += self.__assess_sys_call_arch(_sub_stash)

            # UMask
            stash += self.__assess_umask(_sub_stash)

            # RemoveIPC
            stash += self.__access_remove_ipc(_sub_stash)

            # RootDirectory/RootImage
            stash += self.__access_rootdir(_sub_stash)

            # ProtectSystem
            stash += self.__access_protect_sys(_sub_stash)

            # ProtectHome
            stash += self.__access_protect_home(_sub_stash)

            # NotifyAccess
            stash += self.__access_notify_access(_sub_stash)

            # KeyringMode
            stash += self.__access_keyring_mode(_sub_stash)

            # IPAddressDeny
            stash += self.__access_ip_deny(_sub_stash)

            # DevicePolicy
            stash += self.__access_device_policy(_sub_stash)

            # Unset values
            stash += self.__access_favor_unset_boolean(
                _sub_stash, ["AmbientCapabilities"])
        return stash


SPECIALS_SINGLEITEM = [
    SpecialTypeOneShotExecStart(),
    SpecialForwardReverseOption()

]

SPECIALS_ALLITEMS = [
    SpecialRestartAlwaysConflicts(),
    SpecialDepCycle(),
    SpecialSecurityAssessment()
]
