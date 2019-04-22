class Setting(object):

    def __init__(self, name=None, section=None, allowedValue=None, sinceRel=None, tillRel=None, requires=None, restricted=None):
        self.Name = name
        self.Section = section
        self.AllowedValue = allowedValue
        self.SinceRel = sinceRel or "0.0"
        self.TillRel = tillRel or "99.99"
        self.Restricted = restricted
        self.Requires = requires