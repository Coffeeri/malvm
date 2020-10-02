"""This module contains classes for characteristics of cpuid hypervisor.

Classes:
    CPUidHypervisorCharacteristic: Checks and Fixes cpuid hypervisor bit in Virtualbox.
"""
import subprocess
from typing import Any

from ..abstract_characteristic import PreBootVMCharacteristic, VMType


class CPUidHypervisorCharacteristic(PreBootVMCharacteristic):
    """Checks and Fixes cpuid hypervisor bit in Virtualbox."""

    def __init__(self):
        super().__init__("CPUID", "Fixes hypervisor bit in cpuid feature bits.")

    def fix(self,) -> Any:
        subprocess.run(
            ["VBoxManage", "modifyvm", self.vm.name, "--paravirtprovider", "none"],
        )
        return self.check()

    def check(self) -> Any:
        """Checks if `paravirtprovider` is none."""
        result = subprocess.run(
            ["VBoxManage", "showvminfo", self.vm.name, "--machinereadable"],
            stdout=subprocess.PIPE,
        )
        return 'paravirtprovider="none"' in result.stdout.decode("utf-8").split("\n")
