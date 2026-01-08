from os import getenv, environ


__OBSTOOL_DEBUG = int(getenv("OBSTOOL_DEBUG", 0))


def set_log_level(level: int):
    global __OBSTOOL_DEBUG
    __OBSTOOL_DEBUG = level
    environ["OBSTOOL_DEBUG"] = str(level)


def debug_log(message: str, obj = None, ex: Exception = None):

    if __OBSTOOL_DEBUG >= 2:
        error_log(message, obj, ex, level="D")


def info_log(message: str, obj = None, ex: Exception = None):

    if __OBSTOOL_DEBUG >= 1:
        error_log(message, obj, ex, level="I")


def error_log(message: str, obj = None, ex: Exception = None, level: str = "E"):

    from datetime import datetime
    from os import getpid
    from traceback import format_exception

    log_header = f"{datetime.now().isoformat(timespec="seconds")} {level[0]} {getpid():07d}"

    print(f"{log_header} {message}")
    if obj is not None:
        print(f"{log_header} ", obj, sep="| ")
    if ex is not None:
        if __OBSTOOL_DEBUG >= 2:
            print(f"{log_header} ", "".join(format_exception(ex, limit=None, chain=True)), sep="| ")
        else:
            print(f"{log_header} ", repr(ex), sep="| ")
    print()
