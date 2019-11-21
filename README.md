# systemdlint

![Build status](https://github.com/priv-kweihmann/systemdlint/workflows/Build/badge.svg)
[![PyPI version](https://badge.fury.io/py/systemdlint.svg)](https://badge.fury.io/py/systemdlint)
[![Python version](https://img.shields.io/pypi/pyversions/systemdlint)](https://img.shields.io/pypi/pyversions/systemdlint)
[![Downloads](https://img.shields.io/pypi/dm/systemdlint)](https://img.shields.io/pypi/dm/systemdlint)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/priv-kweihmann/systemdlint.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/priv-kweihmann/systemdlint/context:python)

Systemd Unitfile Linter

## Usage

```sh
usage: systemdlint [-h] [--nodropins] [--rootpath ROOTPATH]
                   [--sversion SVERSION] [--output OUTPUT]
                   files [files ...]

Systemd Unitfile Linter

positional arguments:
  files                Files to parse

optional arguments:
  -h, --help           show this help message and exit
  --nodropins          Ignore Drop-Ins for parsing
  --rootpath ROOTPATH  Root path
  --sversion SVERSION  Version of Systemd to be used
  --output OUTPUT      Where to flush the findings (default: stderr)
```

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
* SettingRequires - The option requires another option to be set
* SettingRestricted - The option can't be set due to another option
* SyntaxError - The file is not parsable
* UnitSectionMissing - The Unit-section is missing in the file
* UnknownUnitType - The file extension of the file is not a known systemd one
* WrongFileMask - The file has a risky filemode set
