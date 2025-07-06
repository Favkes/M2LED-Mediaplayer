import datetime


_colors = {
    'red':      '\x1b[1;31;40m',
    'green':    '\x1b[1;32;40m',
    'yellow':   '\x1b[1;33;40m',
    'blue':     '\x1b[1;34;40m',
    'none':     '\x1b[0m'
}


def log(msg: str, col: str = 'none') -> None:
    print(
        datetime.datetime.now().strftime('%H:%M:%S'),
        _colors[col] + msg + _colors['none']
    )
