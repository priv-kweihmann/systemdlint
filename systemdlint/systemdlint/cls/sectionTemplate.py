from typing import List, Type
from systemdlint.cls.attributeTemplate import AttributeTemplate
from systemdlint.cls.helper import Helper
from systemdlint.cls.error import Error, ErrorInvalidSetting


class SectionTemplate():
    def __init__(self, name: str, version: int = 10e9) -> None:
        self.__name = name
        self.__runversion = version

        self.__attributes = self.__load_attributes()
        self.__available_attributes = self.__attributes

        self.__attribute_map = {
            x.Name: x for x in self.__available_attributes
        }

    def __load_attributes(self) -> List[AttributeTemplate]:
        seen_objects = set()

        def callback(obj: SectionTemplate, type: Type) -> object:
            try:
                res = type.get_applicable(maxver=self.__runversion)()
                if res.Name not in seen_objects:
                    seen_objects.add(res.Name)
                    return res
                return None
            except:
                return None
        return Helper.GetSubClasses(self, callback, 'attributes/*.py')

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def AvailableAttributes(self) -> List[AttributeTemplate]:
        return self.__available_attributes

    def Validate(self, fn: str, attribute: str, value: str, stash: List[object]) -> List[Error]:
        obj = self.__attribute_map.get(attribute, None)
        if obj is None:
            return [ErrorInvalidSetting(attribute, self.Name, 1, fn)]
        return obj.Validate(fn, value, stash)

    def __repr__(self) -> str:
        return f'{self.Name}: {self.AvailableAttributes}'
