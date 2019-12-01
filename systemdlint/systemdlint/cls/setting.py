class Setting(object):

    def __init__(self, name=None, section=None, allowedValue=None, sinceRel=None, tillRel=None, requires=[], restricted=[], dropinproc=None):
        self.Name = name
        self.Section = section
        self.AllowedValue = allowedValue
        self.SinceRel = sinceRel or "0.0"
        self.TillRel = tillRel or "99.99"
        self.Restricted = restricted
        self.Requires = requires
        self.DropinProc = dropinproc or DropinOverride()


class DropinOverride(object):
    def Run(self, unit, stash):
        stash.append(unit)
        return stash


class DropinAdditive(object):
    def Run(self, unit, stash):
        if not unit.Value.strip():
            # remove all setting with same Section and Key
            # in before from stash
            stash = [x for x in stash if not (
                x.Section == unit.Section and x.Key == unit.Key)]
        stash.append(unit)
        return stash
