"""This module contains classes for characteristics of VideoBiosString."""

import subprocess

from ..abstract_characteristic import Characteristic, CheckResult, CheckType


class VideoBiosString(Characteristic):
    """Renames the BiosString of the video card."""

    def __init__(self) -> None:
        super().__init__("VBIOS", "Renames the BiosString of the video card.")

    def fix(self) -> CheckResult:
        biosstring_one = r"BiosString = ((Get-ItemProperty " \
                         r"-path 'HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000')" \
                         r".'HardwareInformation.BiosString'); " \
                         r"if (BiosString -eq 'Oracle VM VirtualBox VBE Adapte'){" \
                         r"New-ItemProperty " \
                         r"-Path HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000 " \
                         r"-Name HardwareInformation.BiosString " \
                         r"-Value 'Intel Corporation'  " \
                         r"-PropertyType 'String' -force }"

        biosstring_two = r"BiosString = ((Get-ItemProperty " \
                         r"-path 'HKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016')" \
                         r".'HardwareInformation.BiosString'); " \
                         r"if (BiosString -eq 'Oracle VM VirtualBox VBE Adapte'){" \
                         r"New-ItemProperty " \
                         r"-Path HKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016 " \
                         r"-Name HardwareInformation.BiosString " \
                         r"-Value 'Intel Corporation'  " \
                         r"-PropertyType 'String' -force }"

        subprocess.run(["powershell", "-Command", biosstring_one], check=False)
        subprocess.run(["powershell", "-Command", biosstring_two], check=False)
        return self.check()

    def check(self) -> CheckResult:
        result_biosstring_one = subprocess.getoutput(
            r"powershell ((Get-ItemProperty "
            r"-path 'HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000')"
            r".'HardwareInformation.BiosString')") != "Oracle VM VirtualBox VBE Adapte"
        result_biosstring_two = subprocess.getoutput(
            r"powershell ((Get-ItemProperty "
            r"-path 'HHKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016')"
            r".'HardwareInformation.BiosString')") != "Oracle VM VirtualBox VBE Adapte"
        yield self, CheckType(self.description, all([result_biosstring_one, result_biosstring_two]))
