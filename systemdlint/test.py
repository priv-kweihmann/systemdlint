from systemdlint.impl.service import ConfigService

x = ConfigService(255)

with open('test.service', 'w') as o:
    o.write('[Unit]\n')
    o.write('Description=Foo\n')
    o.write('[Service]\n')
    o.write('Description=Foo\n')
    o.write('[Bar]\n')

    o.flush()

    if x.Matches('test.service'):
        for item in x.Parse('test.service'):
            print(item)