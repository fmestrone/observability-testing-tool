from os import getenv, environ


__OBSTOOL_DEBUG = int(getenv("OBSTOOL_DEBUG", 0))
def set_skip_schema(skip: bool):
    if skip:
        environ["OBSTOOL_SKIP_VALIDATION"] = "True"
    else:
        environ["OBSTOOL_SKIP_VALIDATION"] = "False"


def should_skip_schema() -> bool:
    return getenv("OBSTOOL_SKIP_VALIDATION") == "True"


def set_log_level(level: int):
    global __OBSTOOL_DEBUG
    __OBSTOOL_DEBUG = level
    environ["OBSTOOL_DEBUG"] = str(level)


def set_dry_run(dry_run: bool):
    if dry_run:
        environ["OBSTOOL_DRY_RUN"] = "True"
    else:
        environ["OBSTOOL_DRY_RUN"] = "False"


def is_dry_run() -> bool:
    return getenv("OBSTOOL_DRY_RUN") == "True"


def set_not_gce(no_meta: bool):
    if no_meta:
        environ["OBSTOOL_NO_GCE_METADATA"] = "True"
    else:
        environ["OBSTOOL_NO_GCE_METADATA"] = "False"


def is_not_gce() -> bool:
    return getenv("OBSTOOL_NO_GCE_METADATA") == "True"


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
