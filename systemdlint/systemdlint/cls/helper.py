import os
class Helper(object):

    @staticmethod
    def GetPath(*args):
        _res = ["/"]
        for i in args:
            if i.startswith("/"):
                _res.append(i[1:])
            else:
                _res.append(i)
        return os.path.join(*_res)

    @staticmethod
    def StripLeftAll(_in, needles):
        while any([_in.startswith(x) for x in needles]):
            for k in needles:
                if _in.startswith(k):
                    _in = _in.lstrip(k)
        return _in