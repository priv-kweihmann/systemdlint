from systemdlint.cls.attributeTemplate import AttributeTemplate
from versionary.decorators import versioned

class Attribute(AttributeTemplate):

    def __init__(self):
        super().__init__(name='Description')

@versioned()
class AttributeV211(Attribute):

    def __init__(self):
        super().__init__()
        self._available = True