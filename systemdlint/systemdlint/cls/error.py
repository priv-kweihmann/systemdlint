class Error(object):

    def __init__(self, severity, msg, details, line, file, rootfs=True):
        self.Severity = severity
        self.Msg = msg
        self.Details = details
        self.Line = line
        self.File = file
        self.RequiresRootfs = rootfs

    def __repr__(self):
        return "{}:{}:{} [{}] - {}".format(self.File, self.Line, self.Severity, self.Msg, self.Details)

    def __eq__(self, other):
        if isinstance(other, Error) or issubclass(other, Error):
            return str(other) == str(self)
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__repr__())


class ErrorDeprecated(Error):
    def __init__(self, object, since, line, file):
        super().__init__("warning", "OptionDeprecated",
                         "{} is deprecated since {}".format(object, since), line, file, rootfs=False)


class ErrorTooNewOption(Error):
    def __init__(self, object, since, line, file):
        super().__init__("warning", "OptionTooNew",
                         "'{}' is only available with version {}+".format(object, since), line, file, rootfs=False)


class ErrorSyntaxError(Error):
    def __init__(self, msg, line, file):
        super().__init__("error", "SyntaxError", msg, line, file, rootfs=False)


class ErrorUnknownUnitType(Error):
    def __init__(self, fileext, file):
        super().__init__("warning", "UnknownUnitType",
                         "The extention '{}' is unknown".format(fileext), 1, file, rootfs=False)


class ErrorFileMaskWrong(Error):
    def __init__(self, current, expected, file):
        super().__init__("warning", "WrongFileMask", "The current filemask '{}' is risky. Please use {}".format(
            oct(current), ",".join([oct(x) for x in expected])), 1, file, rootfs=False)


class ErrorUnitSectionMissing(Error):
    def __init__(self, file):
        super().__init__("error", "UnitSectionMissing",
                         "[Unit]-Section is missing in file", 1, file, rootfs=False)


class ErrorMountUnitNaming(Error):
    def __init__(self, correct, file):
        super().__init__("error", "MountUnitNaming",
                         "The mount unit should be named '{}.mount'".format(correct), 1, file, rootfs=False)


class ErrorRefUnitNotFound(Error):
    def __init__(self, unit, line, file):
        super().__init__("warning", "ReferencedUnitNotFound",
                         "The Unit '{}' referenced was not found in filesystem".format(unit), line, file)


class ErrorMandatoryOptionMissing(Error):
    def __init__(self, option, section, file):
        super().__init__("error", "MandatoryOptionMissing",
                         "Mandatory option '{}' is missing in section [{}]".format(option, section), 1, file, rootfs=False)


class ErrorInvalidValue(Error):
    def __init__(self, object, value, line, file):
        super().__init__("error", "InvalidValue", "{}={}".format(object, value), line, file, rootfs=False)


class ErrorInvalidNumericBase(Error):

    def __init__(self, object, base, line, file):
        super().__init__("error", "InvalidNumericBase",
                         "{} must be a multiple of {}".format(object, base), line, file, rootfs=False)


class ErrorSettingRequires(Error):

    def __init__(self, object, limitation, line, file):
        super().__init__("error", "SettingRequires",
                         "{} requires {}".format(object, limitation), line, file, rootfs=False)


class ErrorSettingRestricted(Error):

    def __init__(self, object, limitation, line, file):
        super().__init__("error", "SettingRestricted",
                         "{} can't be set when {}".format(object, limitation), line, file, rootfs=False)


class ErrorInvalidSetting(Error):

    def __init__(self, object, section, line, file):
        super().__init__("error", "InvalidSetting",
                         "{} is not supported in section {}".format(object, section), line, file, rootfs=False)


class ErrorCommandCouldFail(Error):

    def __init__(self, line, file):
        super().__init__("info", "NoFailureCheck",
                         "Return-code check is disabled. Errors are not reported", line, file, rootfs=False)


class ErrorCommandFullPrivileges(Error):

    def __init__(self, line, file):
        super().__init__("info", "FullPrivileges",
                         "Command is run with full privileges. Use with caution", line, file, rootfs=False)


class ErrorNoExecutable(Error):

    def __init__(self, line, file):
        super().__init__("error", "NoExecutable", "Command is not an executable", line, file)


class ErrorExecNotFound(Error):

    def __init__(self, line, file):
        super().__init__("error", "ExecNotFound", "Command referenced not found", line, file)


class ErrorMultiplicity(Error):

    def __init__(self, msg, line, file):
        super().__init__("error", "Multiplicity", msg, line, file, rootfs=False)


class ErrorConflictingOptions(Error):

    def __init__(self, msg, line, file):
        super().__init__("warning", "ConflictingOptions", msg, line, file, rootfs=False)


class ErrorCyclicDependency(Error):
    def __init__(self, depchain, line, file):
        super().__init__("error", "ErrorCyclicDependency",
                         "Unit creates a cyclic dependency. Chain is {}".format("->".join(depchain)), line, file)

class ErrorSecurity(Error):
    def __init__(self, msg, file, subid, line=1, severity="error"):
        super().__init__(severity, "Security.{}".format(subid), msg, line, file, rootfs=False)