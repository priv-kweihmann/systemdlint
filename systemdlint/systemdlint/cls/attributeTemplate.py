from typing import List
from systemdlint.cls.value import Value
from systemdlint.cls.limitation import Limitation
from systemdlint.cls.error import Error

class AttributeTemplate():

    def __init__(self, name: str = None, allowed_value: Value = None,
                 available: bool = False, deprecated: bool = False,
                 requires: List[Limitation] = None,
                 restricted: List[Limitation] = None,
                 additive_dropin: bool = False):
        self.__name = name
        self._allowed_value = allowed_value
        self._available = available
        self._deprecated = deprecated
        self._restricted = restricted or []
        self._requires = requires or []
        self._dropinproc = DropinAdditive() if additive_dropin else DropinOverride()

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def AllowedValue(self) -> Value:
        return self._allowed_value

    @property
    def Available(self) -> bool:
        return self._available

    @property
    def Deprecated(self) -> bool:
        return self._deprecated

    @property
    def Restricted(self) -> List[Limitation]:
        return self._restricted

    @property
    def Requires(self) -> List[Limitation]:
        return self._requires

    def __repr__(self) -> str:
        return f'{self.Name}:{self.__version__}'

    def Validate(self, fn: str, value: str, stash: List[object]) -> List[Error]:
        return []


class DropinOverride():
    def Run(self, unit, stash):
        stash.append(unit)
        return stash


class DropinAdditive():
    def Run(self, unit, stash):
        if not unit.Value.strip():
            # remove all setting with same Section and Key
            # in before from stash
            stash = [x for x in stash if not (
                x.Section == unit.Section and x.Key == unit.Key)]
        stash.append(unit)
        return stash
