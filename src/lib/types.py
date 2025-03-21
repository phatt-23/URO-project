from typing import Any, Dict, Type, TypeVar, cast

T = TypeVar("T", bound="SingletonMeta")

class SingletonMeta(type):
    _instances: Dict[Type[Any], Any] = {}

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cast(T, cls._instances[cls])


class Singleton(metaclass=SingletonMeta):
    pass
