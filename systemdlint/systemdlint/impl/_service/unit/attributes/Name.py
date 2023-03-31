from systemdlint.cls.attributeTemplate import AttributeTemplate
from versionary.decorators import versioned

class Attribute(AttributeTemplate):

    def __init__(self):
        super().__init__(name='Name')

@versioned()
class AttributeV250(Attribute):

    def __init__(self):
        super().__init__()
        self._available = True

@versioned()
class AttributeV251(Attribute):

    def __init__(self):
        super().__init__()
        self._available = True
