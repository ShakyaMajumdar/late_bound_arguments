__version__ = '0.1.0'

import inspect
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

_SENTINEL = object()


_P = ParamSpec("_P")
_T = TypeVar("_T")


def delay(*params_to_delay: str) -> Callable[_P, Callable[_P, _T]]:

    def deco(func: Callable[_P, _T]) -> Callable[_P, _T]:
        sig = inspect.signature(func)
        if not set(params_to_delay) <= sig.parameters.keys():
            raise TypeError(
                f"args {set(params_to_delay) - sig.parameters.keys()} missing in signature"
            )

        defaults: dict[str, str] = {}
        for param in params_to_delay:
            default = sig.parameters[param].default
            if default == inspect.Parameter.empty:
                raise TypeError(f"parameter {param} has no default value")
            defaults[param] = default

        sig = sig.replace(
            parameters=[
                v
                if k not in params_to_delay
                else inspect.Parameter(
                    v.name, v.kind, default=_SENTINEL, annotation=v.annotation
                )
                for k, v in sig.parameters.items()
            ]
        )

        @wraps(func)
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            actual = sig.bind(*args, **kwargs)
            actual.apply_defaults()
            args_so_far = {}
            for k, v in actual.arguments.items():
                if v is _SENTINEL:
                    try:
                        actual.arguments[k] = eval(defaults[k], globals(), args_so_far)
                    except NameError as e:
                        if e.name in actual.arguments:
                            raise TypeError("tried to reference argument later in signature")
                        else:
                            raise
                    args_so_far[k] = actual.arguments[k]
                else:
                    args_so_far[k] = v
            return func(*actual.args, **actual.kwargs)

        return inner

    return deco
