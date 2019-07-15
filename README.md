# systemdlint
Systemd Unitfile Linter

# Usage
```
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

# Output

The tool will return 

    {file}:{line}:{severity} [{id}] - {message}

example:
```
/lib/systemd/system/console-shell.service:18:info [NoFailureCheck] - Return-code check is disabled. Errors are not reported
/lib/systemd/system/plymouth-halt.service:11:info [NoFailureCheck] - Return-code check is disabled. Errors are not reported
/lib/systemd/system/systemd-ask-password-console.service:12:warning [ReferencedUnitNotFound] - The Unit 'systemd-vconsole-setup.service' referenced was not found in filesystem
/lib/systemd/system/basic.target:19:warning [ReferencedUnitNotFound] - The Unit 'tmp.mount' referenced was not found in filesystem
```

# Detectable Errors

 * ConflictingOptions - The set option somehow is in conflict with another unit
 * ExecNotFound - The referenced executable was not found on system
 * FullPrivileges - An executable is run with full priviledges
 * InvalidNumericBase - A numeric value doesn't match because it needs to be a multiple of X
 * InvalidSetting - The option doesn't match the section
 * InvalidValue - An invalid value is set
 * MandatoryOptionMissing - A mandatory option was missing in the file
 * Multiplicity - The option is not valid for the given amount of options in this context
 * NoExecutable - The referenced executable is NOT executable
 * NoFailureCheck - An executable is run without checking for failures 
 * OptionDeprecated - The used option is not available anymore in this version
 * OptionTooNew - The used option will be avaiable in a later version than used
 * ReferencedUnitNotFound - The unit referenced was not found in system
 * SettingRequires - The option requires another option to be set
 * SettingRestricted - The option can't be set due to another option
 * SyntaxError - The file is not parseable 
 * UnitSectionMissing - The Unit-section is missing in the file
 * UnknownUnitType - The file extension of the file is not a known systemd one
 * WrongFileMask - The file has a risky filemode set

