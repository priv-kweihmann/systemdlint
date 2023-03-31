from systemdlint.impl.service import ConfigService

x = ConfigService(255)
print(x)
print(x.Validate('foo', 'bar', '123', []))
print(x.Validate('Service', 'Type', '123', []))
print(x.Validate('Unit', 'Name', '123', []))