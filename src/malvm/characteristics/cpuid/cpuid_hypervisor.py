"""This module contains classes for characteristics of cpuid hypervisor.

Classes:
    CPUidHypervisorCharacteristic: Checks and Fixes cpuid hypervisor bit in Virtualbox.
"""
import logging

from ..abstract_characteristic import CheckResult, CheckType, PreBootCharacteristic
from ...utils.helper_methods import get_virtual_box_vminfo, run_external_program_no_return

log = logging.getLogger()


class CPUidHypervisorCharacteristic(PreBootCharacteristic):
    """Checks and Fixes cpuid hypervisor bit in Virtualbox."""

    def __init__(self):
        super().__init__("CPUID", "Hypervisor bit in cpuid feature bits.")

    def fix(self) -> CheckResult:
        vm_name = self.environment.vm_name
        if vm_name:
            log.debug(f"Run VBoxManage modifyvm {vm_name} --paravirtprovider none")
            run_external_program_no_return("VBoxManage", "modifyvm", vm_name, "--paravirtprovider", "none")
        return self.check()

    def check(self) -> CheckResult:
        # pylint:
        """Checks if `paravirtprovider` is none."""
        vm_name = self.environment.vm_name
        if vm_name:
            result = get_virtual_box_vminfo(vm_name)
            self.is_fixed = 'paravirtprovider="none"' in result.stdout.decode("utf-8").split("\n")
        yield self, CheckType(self.description, self.is_fixed)
