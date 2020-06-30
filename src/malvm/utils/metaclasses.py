"""This Module contains helper metaclasses."""

from typing import Any, Dict, Mapping, Sequence, Type


class SingletonMeta(type):
    """Singleton Metaclass.

    All classes inheriting from SingletonMeta can be instantiated once.
    """

    _instances: Dict["SingletonMeta", Type["SingletonMeta"]] = {}

    def __call__(
        cls, *args: Sequence[Any], **kwargs: Mapping[Any, Any]
    ) -> Type["SingletonMeta"]:
        """Returns the instance of the class.

        Creates an instance of a class if it does not exist yet.

        Args:
            cls (SingletonMeta): Class which is defined by inheritance.
            *args (Sequence[Any]): Arguments for class.__call__.
            **kwargs (Mapping[Any, Any]): Keyword arguments for class.__call__.

        Returns:
            Type[SingletonMeta]: Instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
