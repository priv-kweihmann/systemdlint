class Limitation(object):

    def __init__(self, key=None, value=None, section=None, file=None):
        self.Key = key
        self.Value = value
        self.Section = None
        self.File = file

    def __repr__(self):
        return "{}={}".format(self.Key, self.Value)

    def Matches(self, stack, parent):
        for element in stack:
            if (element.File == parent.File or self.File == "ignore") and \
               element.Section == (self.Section or parent.Section) and \
               element.Key == self.Key:
                if not self.Value:
                    # Wildcard
                    return True
                if isinstance(self.Value, tuple) or isinstance(self.Value, list):
                    return element.Value in self.Value
                return element.Value == self.Value
        return False

    def GetChunks(self):
        res = []
        _x = self.Value
        if not isinstance(self.Value, tuple) and not isinstance(self.Value, list):
            _x = [self.Value]
        for x in _x:
            _res = []
            if self.Section:
                _res.append("[{}]".format(self.Section))
            _res.append("{}={}".format(self.Key, x))
            res.append(_res)
        return res
