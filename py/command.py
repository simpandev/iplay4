import functools
from typing import Any, Callable, Dict

__author__ = "Simone Pandolfi <simopandolfi@gmail.com>"
__version__ = (1, 0, 0, "benjamino")


Commands = Dict[str, Callable[[Any], Any]]
Schema = Dict[str, Commands]

SCHEMA: Schema = {}


def command(schema: str, cmd: str) -> Callable[[Any], Any]:

    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)
        
        _schema = SCHEMA.setdefault(schema, {})
        _schema[cmd] = wrapper

        return wrapper
    
    return decorator
