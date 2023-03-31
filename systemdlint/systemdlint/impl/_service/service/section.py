from systemdlint.cls.sectionTemplate import SectionTemplate

class Section(SectionTemplate):

    def __init__(self, version: int) -> None:
        super().__init__('Service', version=version)