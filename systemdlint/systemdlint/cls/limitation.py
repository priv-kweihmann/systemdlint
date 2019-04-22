class Limitation(object):

    def __init__(self, key=None, value=None):
        self.Key = key
        self.Value = value

    def __repr__(self):
        return "{}={}".format(self.Key, self.Value)
    
    def Matches(self, stack, parent):
        for element in stack:
            if element.File == parent.File and \
               element.Section == parent.Section and \
               element.Key == self.Key:
               if not self.Value:
                   ## Wildcard
                   return True
               if isinstance(self.Value, tuple) or isinstance(self.Value, list):
                   return element.Value in self.Value
               return element.Value == self.Value
        return False
