from systemdlint.cls.configTemplate import ConfigTemplate


class ConfigService(ConfigTemplate):

    def __init__(self, version: int) -> None:
        super().__init__('service',
                         ['/etc/systemd/system/*.service', '*.service'],
                         [], ['Service', 'Unit'],
                         version=version)
