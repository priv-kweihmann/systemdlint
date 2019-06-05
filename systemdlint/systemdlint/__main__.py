from systemdlint.cls.parser import Parser
from systemdlint.cls.runargs import ArgParser

if __name__ == '__main__':
    runargs = ArgParser()
    _parser = Parser(runargs, runargs.files)
    _errors = []
    _stash = _parser.GetResults()
    for item in _stash:
        _errors += item.Validate(runargs, _stash)
    _errors = list(set(_errors))
    
    _out = runargs.output
    if isinstance(_out, str):
        _out = open(runargs.output, "w")
    for item in _errors:
        _out.write(str(item) + "\n")