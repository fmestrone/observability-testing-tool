def debug_log(message: str, object: any = None, exception: Exception = None):

    from datetime import datetime
    from os import getenv, getpid
    from traceback import format_exception

    if getenv("ADVOBS_DEBUG") == "True":
        print(f"{datetime.now().isoformat(timespec="seconds")} {getpid()} {message}")
        if object is not None:
            print(object)
        if exception is not None:
            print("".join(format_exception(exception, limit=None, chain=True)))
        print()
