"""This initializes the characteristics package and automatically loads all of them."""
import inspect
import pkgutil
import sys
from importlib import import_module
from pathlib import Path

from .abstract_characteristic import Characteristic, PreBootVMCharacteristic

loaded_characteristics = []
loaded_pre_boot_characteristics = []
for (_, name, _) in pkgutil.iter_modules([str(Path(__file__).parent)]):
    imported_module = import_module("." + name, package=__name__)
    imported_module = import_module(f"{__name__}.{name}")
    for i in dir(imported_module):
        attribute = getattr(imported_module, i)

        if (
            inspect.isclass(attribute)
            and issubclass(attribute, Characteristic)
            and attribute is not Characteristic
        ):
            setattr(sys.modules[__name__], name, attribute)
            loaded_characteristics.append(attribute)
        elif (
            inspect.isclass(attribute)
            and issubclass(attribute, PreBootVMCharacteristic)
            and attribute is not PreBootVMCharacteristic
        ):
            setattr(sys.modules[__name__], name, attribute)
            loaded_pre_boot_characteristics.append(attribute)
