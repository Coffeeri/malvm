"""PyTest tests for FileVBCharacteristic class."""
from pathlib import Path
from typing import List, Tuple

from malvm.characteristics.abstract_characteristic import LambdaCharacteristic
from malvm.characteristics.files import FileVBCharacteristic
from malvm.utils.helper_methods import get_project_root
from malvm.controller.virtual_machine.hypervisor.virtualbox.vagrant import read_json_file


def test_characteristic_init() -> None:
    """Tests if FileVBCharacteristic initializes the correct sub_characteristics."""
    characteristic = FileVBCharacteristic()
    sub_characteristics_from_file = read_json_file(
        (Path(Path(get_project_root() / "data/files_virtualbox.json")).absolute())
    )
    sub_characteristics_from_file = list(sub_characteristics_from_file["files"])
    sub_characteristics: List[Tuple[str, LambdaCharacteristic]] = [
        (c.slug, c.value) for c in characteristic.sub_characteristics.values()
    ]
    for index, characteristic_file in enumerate(sub_characteristics_from_file):
        assert characteristic_file[0] == sub_characteristics[index][0]
        assert characteristic_file[1] == sub_characteristics[index][1]
