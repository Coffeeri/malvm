"""This module contains classes for characteristics of cpuid hypervisor.

Classes:
    CPUidHypervisorCharacteristic: Checks and Fixes cpuid hypervisor bit in Virtualbox.
"""
import logging
import subprocess
from typing import Optional

from ..abstract_characteristic import (
    Characteristic,
    CharacteristicAttributes,
    CheckType,
    CheckResult,
    Runtime,
)

log = logging.getLogger()


class CPUidHypervisorCharacteristic(Characteristic):
    """Checks and Fixes cpuid hypervisor bit in Virtualbox."""

    def __init__(self):
        super().__init__(
            "CPUID",
            "Hypervisor bit in cpuid feature bits.",
            CharacteristicAttributes(runtime=Runtime.PRE_BOOT),
        )

    def fix(self) -> CheckResult:
        vm_name = self.get_vm_name()
        if vm_name:
            log.debug(f"Run VBoxManage modifyvm {vm_name} --paravirtprovider none")
            subprocess.run(
                ["VBoxManage", "modifyvm", vm_name, "--paravirtprovider", "none"],
                check=True,
            )
        return self.check()

    def check(self) -> CheckResult:
        """Checks if `paravirtprovider` is none."""
        vm_name = self.get_vm_name()
        is_fixed: bool = False
        if vm_name:
            log.debug(f"Run VBoxManage showvminfo {vm_name} --machinereadable")
            result = subprocess.run(
                ["VBoxManage", "showvminfo", vm_name, "--machinereadable"],
                stdout=subprocess.PIPE,
                check=True,
            )
            is_fixed = 'paravirtprovider="none"' in result.stdout.decode("utf-8").split(
                "\n"
            )
        yield self, CheckType(self.description, is_fixed)

    def get_vm_name(self) -> Optional[str]:
        """Returns the Virtual Machine name if set."""
        if "vm_name" not in self.environment:
            return None
        return self.environment["vm_name"]
