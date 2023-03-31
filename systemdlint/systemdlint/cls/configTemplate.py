import fnmatch
from typing import List, Type

from systemdlint.cls.sectionTemplate import SectionTemplate
from systemdlint.cls.helper import Helper
from systemdlint.cls.error import Error, ErrorInvalidSection


class ConfigTemplate():

    def __init__(self, name: str, globs: List[str],
                 upstream_inputs: List[str] = None,
                 mandatory_sections: List[str] = None,
                 version: int = 10e9) -> None:
        self.__name = name
        self.__runversion = version
        self.__applicable_globs = globs
        self.__upstream_generator_inputs = upstream_inputs

        self.__mandatory_sections = mandatory_sections
        self.__sections = self.__load_sections()
        self.__section_map = {
            x.Name: x for x in self.__sections
        }

    def __load_sections(self) -> List[SectionTemplate]:
        def callback(obj: ConfigTemplate, type: Type) -> object:
            if not issubclass(type, SectionTemplate):
                return None
            if type is SectionTemplate:
                return None
            return type(self.__runversion)
        return Helper.GetSubClasses(self, callback, f'_{self.Name}/*/section.py')

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def ApplicableGlobs(self) -> List[str]:
        return self.__applicable_globs

    @property
    def Sections(self) -> List[SectionTemplate]:
        return self.__sections

    @property
    def MandatorySections(self) -> List[str]:
        return self.__mandatory_sections

    @property
    def UpstreamGeneratorInput(self) -> List[str]:
        return self.__upstream_generator_inputs

    def Matches(self, fn) -> bool:
        for pattern in self.ApplicableGlobs:
            if fnmatch.fnmatch(fn, pattern):
                return True
        return False

    def Validate(self, section: str, attribute: str, value: str, stash: List[object]) -> List[Error]:
        obj = self.__section_map.get(section, None)
        if obj is None:
            return ErrorInvalidSection(section, 1, 1)
        return obj.Validate(attribute, value, stash)

    def __repr__(self):
        return f'{self.Name} -> {self.Sections}'
