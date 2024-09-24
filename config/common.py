from os import getenv


__ADVOBS_DEBUG = (getenv("ADVOBS_DEBUG") == "True")


def debug_log(message: str, object: any = None, exception: Exception = None):
    if __ADVOBS_DEBUG:
        info_log(message, object, exception, level="D")


def info_log(message: str, object: any = None, exception: Exception = None, level: str = "I"):

    from datetime import datetime
    from os import getpid
    from traceback import format_exception

    log_header = f"{datetime.now().isoformat(timespec="seconds")} {level[0]} {getpid():07d}"

    print(f"{log_header} {message}")
    if object is not None:
        print(f"{log_header} ", object)
    if exception is not None:
        print(f"{log_header} ", "".join(format_exception(exception, limit=None, chain=True)))
    print()
