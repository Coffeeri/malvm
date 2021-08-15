"""This module contains classes for characteristics of VideoChipType."""

import subprocess

from ..abstract_characteristic import Characteristic, CheckResult, CheckType


class VideoChipType(Characteristic):
    """Renames the ChipType of VirtualBox VESA BIOS."""

    def __init__(self) -> None:
        super().__init__("CHIP", "Renames the ChipType of VirtualBox VESA BIOS.")

    def fix(self) -> CheckResult:
        chiptype_one = r"ChipType = ((Get-ItemProperty " \
                       r"-path 'HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000')" \
                       r".'HardwareInformation.ChipType'); " \
                       r"if (ChipType -eq 'VirtualBox VESA BIOS'){" \
                       r"New-ItemProperty " \
                       r"-Path HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000 " \
                       r"-Name HardwareInformation.ChipType " \
                       r"-Value 'Intel Corporation' " \
                       r"-PropertyType 'String' -force }"

        chiptype_two = r"ChipType = ((Get-ItemProperty " \
                       r"-path 'HKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016')" \
                       r".'HardwareInformation.ChipType'); " \
                       r"if (ChipType -eq 'VirtualBox VESA BIOS'){" \
                       r"New-ItemProperty " \
                       r"-Path HKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016 " \
                       r"-Name HardwareInformation.ChipType " \
                       r"-Value 'Intel Corporation'  " \
                       r"-PropertyType 'String' -force }"

        subprocess.run(["powershell", "-Command", chiptype_one], check=False)
        subprocess.run(["powershell", "-Command", chiptype_two], check=False)
        return self.check()

    def check(self) -> CheckResult:
        result_chiptype_one = subprocess.getoutput(
            r"powershell ((Get-ItemProperty "
            r"-path 'HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000')"
            r".'HardwareInformation.ChipType')") != "VirtualBox VESA BIOS"
        result_chiptype_two = subprocess.getoutput(
            r"powershell ((Get-ItemProperty "
            r"-path 'HHKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016')"
            r".'HardwareInformation.ChipType')") != "VirtualBox VESA BIOS"
        yield self, CheckType(self.description, all([result_chiptype_one, result_chiptype_two]))
