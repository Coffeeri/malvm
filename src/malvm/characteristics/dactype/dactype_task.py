"""This module contains classes for characteristics of OS install date.

Classes:
    OSInstallDate: Changes the os install date to an older one.
"""
import subprocess

from ..abstract_characteristic import Characteristic, CheckResult, CheckType


class DACType(Characteristic):
    """Renames the DACType of Oracle Corporation."""

    def __init__(self) -> None:
        super().__init__("DAC", "Renames the DACType of Oracle Corporation.")

    def fix(self) -> CheckResult:
        dactype_one = r"$DacType = ((Get-ItemProperty " \
                      r"-path 'HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000')" \
                      r".'HardwareInformation.DacType'); " \
                      r"if ($DacType -eq 'Oracle Corporation'){" \
                      r"New-ItemProperty " \
                      r"-Path HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000 " \
                      r"-Name HardwareInformation.DacType " \
                      r"-Value 'Intel Corporation'  " \
                      r"-PropertyType 'String' -force }"

        dactype_two = r"$DacType = ((Get-ItemProperty " \
                      r"-path 'HKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016')" \
                      r".'HardwareInformation.DacType'); " \
                      r"if ($DacType -eq 'Oracle Corporation'){" \
                      r"New-ItemProperty " \
                      r"-Path HKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016 " \
                      r"-Name HardwareInformation.DacType " \
                      r"-Value 'Intel Corporation'  " \
                      r"-PropertyType 'String' -force }"

        subprocess.run(["powershell", "-Command", dactype_one], check=False)
        subprocess.run(["powershell", "-Command", dactype_two], check=False)
        return self.check()

    def check(self) -> CheckResult:
        result_dactype_one = subprocess.getoutput(
            r"powershell ((Get-ItemProperty "
            r"-path 'HKLM:\SYSTEM\CurrentControlSet\Control\Video\*\\0000')"
            r".'HardwareInformation.DacType')") != "Oracle Corporation"
        result_dactype_two = subprocess.getoutput(
            r"powershell ((Get-ItemProperty "
            r"-path 'HHKLM:\SYSTEM\ControlSet001\Control\Class\*\\0016')"
            r".'HardwareInformation.DacType')") != "Oracle Corporation"
        yield self, CheckType(self.description, all([result_dactype_one, result_dactype_two]))
