import datetime


_colors = {
    'red':      '\x1b[1;31;40m',
    'green':    '\x1b[1;32;40m',
    'yellow':   '\x1b[1;33;40m',
    'blue':     '\x1b[1;34;40m',
    'purple':   '\x1b[1;35;40m',
    'grey':     '\x1b[2;37;40m',
    'orange':   '\x1b[1;31;43m',
    'inverted-red': '\x1b[3;30;41m',
    'none':     '\x1b[0m'
}


class Logtype:
    kill    = 'red'
    create  = 'green'
    init    = 'yellow'
    info    = 'grey'
    error   = 'inverted-red'
    warning = 'orange'
    none    = 'none'


class Logger:
    module_name: str
    module_colour: str

    def __init__(self, module_name: str, module_colour: str = 'none'):
        self.module_name = '[' + module_name + '] '
        self.module_col = module_colour

    def log(self, msg: str, code: str = Logtype.none) -> None:
        print(
            _colors['grey']
            + datetime.datetime.now().strftime('%H:%M:%S')
            + _colors[self.module_col]
            + f" {self.module_name:<20}"
            + _colors[code]
            + msg
            + _colors['none']
        )
