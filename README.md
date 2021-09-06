# systemdlint

![Build status](https://github.com/priv-kweihmann/systemdlint/workflows/Build/badge.svg)
[![PyPI version](https://badge.fury.io/py/systemdlint.svg)](https://badge.fury.io/py/systemdlint)
[![Python version](https://img.shields.io/pypi/pyversions/systemdlint)](https://img.shields.io/pypi/pyversions/systemdlint)
[![Downloads](https://img.shields.io/pypi/dm/systemdlint)](https://img.shields.io/pypi/dm/systemdlint)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/priv-kweihmann/systemdlint.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/priv-kweihmann/systemdlint/context:python)

Systemd Unitfile Linter

## Usage

```sh
usage: systemdlint [-h] [--nodropins] [--rootpath ROOTPATH] [--sversion SVERSION] [--output OUTPUT] [--norootfs] files [files ...]

Systemd Unitfile Linter

positional arguments:
  files                Files to parse

optional arguments:
  -h, --help           show this help message and exit
  --nodropins          Ignore Drop-Ins for parsing
  --rootpath ROOTPATH  Root path
  --sversion SVERSION  Version of Systemd to be used
  --output OUTPUT      Where to flush the findings (default: stderr)
  --norootfs           Run only unit file related tests
```

## Why should I use it?

Surely you can use `systemd-analyze verify [unitname]` to validate your units - no problem and it's
the recommended way if you writing units for the system you are currently running on.
Unfortunately systemd doesn't offer a validation which doesn't require an already running version of
systemd you want to validate against.

This tool was initially created to check units in cross-compiled embedded images at build time,
where you can't run a copy of systemd (as it's cross-compiled).
As a consequence it doesn't use any systemd code and might interpret some settings differently than
systemd itself - as with every linter take the outcomes as a basis for further analysis.
Also keep in mind, that systemd does create a larger stack of runtime files, which are not
taken into account by the tool - same for kernel related information like /dev, /sys or /proc
entries.

Furthermore the tool gives you advice how your unit files could be hardened.

## Installation

### PyPi

simply run

```sh
pip3 install systemdlint
```

### From source

* Install the needed requirements by running ```pip3 install systemdunitparser anytree```
* git clone this repository
* cd to \<clone folder\>/systemdlint
* run ```sudo ./build.sh```

## Output

The tool will return

```sh
{file}:{line}:{severity} [{id}] - {message}
```

example:

```sh
/lib/systemd/system/console-shell.service:18:info [NoFailureCheck] - Return-code check is disabled. Errors are not reported
/lib/systemd/system/plymouth-halt.service:11:info [NoFailureCheck] - Return-code check is disabled. Errors are not reported
/lib/systemd/system/systemd-ask-password-console.service:12:warning [ReferencedUnitNotFound] - The Unit 'systemd-vconsole-setup.service' referenced was not found in filesystem
/lib/systemd/system/basic.target:19:warning [ReferencedUnitNotFound] - The Unit 'tmp.mount' referenced was not found in filesystem
```

## Detectable Errors

* ConflictingOptions - The set option somehow is in conflict with another unit
* ErrorCyclicDependency - Unit creates a cyclic dependency
* ExecNotFound - The referenced executable was not found on system
* FullPrivileges - An executable is run with full privileges
* InvalidNumericBase - A numeric value doesn't match because it needs to be a multiple of X
* InvalidSetting - The option doesn't match the section
* InvalidValue - An invalid value is set
* MandatoryOptionMissing - A mandatory option was missing in the file
* Multiplicity - The option is not valid for the given amount of options in this context
* NoExecutable - The referenced executable is NOT executable
* NoFailureCheck - An executable is run without checking for failures
* OptionDeprecated - The used option is not available anymore in this version
* OptionTooNew - The used option will be available in a later version than used
* ReferencedUnitNotFound - The unit referenced was not found in system
* Security.@clock - SystemCallFilter shouldn't contain @clock 
* Security.@cpu-emulation - SystemCallFilter shouldn't contain @cpu-emulation 
* Security.@debug - SystemCallFilter shouldn't contain @debug 
* Security.@module - SystemCallFilter shouldn't contain @module 
* Security.@mount - SystemCallFilter shouldn't contain @mount 
* Security.@obsolete - SystemCallFilter shouldn't contain @obsolete
* Security.@privileged - SystemCallFilter shouldn't contain @privileged 
* Security.@raw-io - SystemCallFilter shouldn't contain @raw-io 
* Security.@reboot - SystemCallFilter shouldn't contain @reboot 
* Security.@resources - SystemCallFilter shouldn't contain @resources 
* Security.@swap - SystemCallFilter shouldn't contain @swap
* Security.AF_INET - RestrictAddressFamilies shouldn't contain AF_INET 
* Security.AF_INET6 - RestrictAddressFamilies shouldn't contain AF_INET6 
* Security.AF_NETLINK - RestrictAddressFamilies shouldn't contain AF_NETLINK 
* Security.AF_PACKET - RestrictAddressFamilies shouldn't contain AF_PACKET 
* Security.AF_UNIX - RestrictAddressFamilies shouldn't contain AF_UNIX
* Security.CAP_AUDIT_CONTROL - CapabilityBoundingSet shouldn't contain CAP_AUDIT_CONTROL 
* Security.CAP_AUDIT_READ - CapabilityBoundingSet shouldn't contain CAP_AUDIT_READ 
* Security.CAP_AUDIT_WRITE - CapabilityBoundingSet shouldn't contain CAP_AUDIT_WRITE 
* Security.CAP_BLOCK_SUSPEND - CapabilityBoundingSet shouldn't contain CAP_BLOCK_SUSPEND
* Security.CAP_CHOWN - CapabilityBoundingSet shouldn't contain CAP_CHOWN 
* Security.CAP_DAC_OVERRIDE - CapabilityBoundingSet shouldn't contain CAP_DAC_OVERRIDE 
* Security.CAP_DAC_READ_SEARCH - CapabilityBoundingSet shouldn't contain CAP_DAC_READ_SEARCH 
* Security.CAP_FOWNER - CapabilityBoundingSet shouldn't contain CAP_FOWNER
* Security.CAP_FSETID - CapabilityBoundingSet shouldn't contain CAP_FSETID 
* Security.CAP_IPC_LOCK - CapabilityBoundingSet shouldn't contain CAP_IPC_LOCK 
* Security.CAP_IPC_OWNER - CapabilityBoundingSet shouldn't contain CAP_IPC_OWNER 
* Security.CAP_KILL - CapabilityBoundingSet shouldn't contain CAP_KILL 
* Security.CAP_LEASE - CapabilityBoundingSet shouldn't contain CAP_LEASE
* Security.CAP_LINUX_IMMUTABLE - CapabilityBoundingSet shouldn't contain CAP_LINUX_IMMUTABLE 
* Security.CAP_MAC_ADMIN - CapabilityBoundingSet shouldn't contain CAP_MAC_ADMIN 
* Security.CAP_MAC_OVERRIDE - CapabilityBoundingSet shouldn't contain CAP_MAC_OVERRIDE 
* Security.CAP_MKNOD - CapabilityBoundingSet shouldn't contain CAP_MKNOD
* Security.CAP_NET_ADMIN - CapabilityBoundingSet shouldn't contain CAP_NET_ADMIN 
* Security.CAP_NET_BIND_SERVICE - CapabilityBoundingSet shouldn't contain CAP_NET_BIND_SERVICE 
* Security.CAP_NET_BROADCAST - CapabilityBoundingSet shouldn't contain CAP_NET_BROADCAST 
* Security.CAP_NET_RAW - CapabilityBoundingSet shouldn't contain CAP_NET_RAW
* Security.CAP_RAWIO - CapabilityBoundingSet shouldn't contain CAP_RAWIO 
* Security.CAP_SETFCAP - CapabilityBoundingSet shouldn't contain CAP_SETFCAP 
* Security.CAP_SETGID - CapabilityBoundingSet shouldn't contain CAP_SETGID 
* Security.CAP_SETPCAP - CapabilityBoundingSet shouldn't contain CAP_SETPCAP 
* Security.CAP_SETUID - CapabilityBoundingSet shouldn't contain CAP_SETUID
* Security.CAP_SYS_ADMIN - CapabilityBoundingSet shouldn't contain CAP_SYS_ADMIN 
* Security.CAP_SYS_BOOT - CapabilityBoundingSet shouldn't contain CAP_SYS_BOOT 
* Security.CAP_SYS_CHROOT - CapabilityBoundingSet shouldn't contain CAP_SYS_CHROOT 
* Security.CAP_SYS_MODULE - CapabilityBoundingSet shouldn't contain CAP_SYS_MODULE
* Security.CAP_SYS_NICE - CapabilityBoundingSet shouldn't contain CAP_SYS_NICE 
* Security.CAP_SYS_PACCT - CapabilityBoundingSet shouldn't contain CAP_SYS_PACCT 
* Security.CAP_SYS_PTRACE - CapabilityBoundingSet shouldn't contain CAP_SYS_PTRACE 
* Security.CAP_SYS_RESOURCE - CapabilityBoundingSet shouldn't contain CAP_SYS_RESOURCE
* Security.CAP_SYS_TIME - CapabilityBoundingSet shouldn't contain CAP_SYS_TIME 
* Security.CAP_SYS_TTY_CONFIG - CapabilityBoundingSet shouldn't contain CAP_SYS_TTY_CONFIG 
* Security.CAP_SYSLOG - CapabilityBoundingSet shouldn't contain CAP_SYSLOG 
* Security.CAP_WAKE_ALARM - CapabilityBoundingSet shouldn't contain CAP_WAKE_ALARM
* Security.CLONE_NEWCGROUP - RestrictNamespaces shouldn't contain CLONE_NEWCGROUP 
* Security.CLONE_NEWIPC - RestrictNamespaces shouldn't contain CLONE_NEWIPC 
* Security.CLONE_NEWNET - RestrictNamespaces shouldn't contain CLONE_NEWNET 
* Security.CLONE_NEWNS - RestrictNamespaces shouldn't contain CLONE_NEWNS
* Security.CLONE_NEWPID - RestrictNamespaces shouldn't contain CLONE_NEWPID 
* Security.CLONE_NEWUSER - RestrictNamespaces shouldn't contain CLONE_NEWUSER 
* Security.CLONE_NEWUTS - RestrictNamespaces shouldn't contain CLONE_NEWUTS
* Security.Delegate - Delegate shall be set to yes 
* Security.DevicePolicy - DevicePolicy should be set to closed
* Security.IPAddressDenyNA - IPAddressDeny shall be set
* Security.KeyringModeNA - KeyringMode shall be set
* Security.KeyringModeNPriv - KeyringMode shall be set to private
* Security.LockPersonality - LockPersonality shall be set to yes 
* Security.MemoryDenyWriteExecute - MemoryDenyWriteExecute shall be set to yes 
* Security.NoNewPrivileges - NoNewPrivileges shall be set to yes
* Security.NotifyAccess - NotifyAccess=all should be avoided
* Security.NoUser - No user is set for the service
* Security.PrivateDevices - PrivateDevices shall be set to yes 
* Security.PrivateMounts - PrivateMounts shall be set to yes 
* Security.PrivateNetwork - PrivateNetwork shall be set to yes 
* Security.PrivateTmp - PrivateTmp shall be set to yes
* Security.PrivateUsers - PrivateUsers shall be set to yes 
* Security.ProtectClock - ProtectClock shall be set to yes 
* Security.ProtectControlGroups - ProtectControlGroups shall be set to yes 
* Security.ProtectHomeNA - ProtectHome shall be set
* Security.ProtectHomeOff - ProtectHome shall be set to yes
* Security.ProtectHostname - ProtectHostname shall be set to yes
* Security.ProtectKernelLogs - ProtectKernelLogs shall be set to yes 
* Security.ProtectKernelModules - ProtectKernelModules shall be set to yes 
* Security.ProtectKernelTunables - ProtectKernelTunables shall be set to yes
* Security.ProtectSystemNA - ProtectSystem shall be set
* Security.ProtectSystemNStrict - ProtectSystem shall be set to strict
* Security.RemoveIPC - RemoveIPC should be activated
* Security.RestrictRealtime - RestrictRealtime shall be set to yes 
* Security.RestrictSUIDSGID - RestrictSUIDSGID shall be set to yes
* Security.RootDirectory - RootDirectory or RootImage shall be set to a non-root path
* Security.SupplementaryGroups - SupplementaryGroups shall be avoided
* Security.SystemCallArchitecturesMult - SystemCallArchitectures shouldn't be set for multiple archs
* Security.SystemCallArchitecturesNA - SystemCallArchitectures shall be set
* Security.UMaskGR - Files created by service are group-readbale
* Security.UMaskGW - Files created by service are group-writeable
* Security.UMaskOR - Files created by service are world-readbale
* Security.UMaskOW - Files created by service are world-writeable
* Security.UserNobody - User nobody is set for the service
* Security.UserRoot - User root is set for the service
* SettingRequires - The option requires another option to be set
* SettingRestricted - The option can't be set due to another option
* SyntaxError - The file is not parsable
* UnitSectionMissing - The Unit-section is missing in the file
* UnknownUnitType - The file extension of the file is not a known systemd one
* WrongFileMask - The file has a risky filemode set

## vscode extension

Find the extension in the [marketplace](https://marketplace.visualstudio.com/items?itemName=kweihmann.systemdlint-vscode), or search for `systemdlint-vscode`
