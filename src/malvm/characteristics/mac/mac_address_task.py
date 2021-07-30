"""This module contains a class for modifying the MAC address of the vagrant management NIC."""

import logging
import random
import re
import subprocess
import uuid

from ..abstract_characteristic import CheckResult, CheckType, PreBootCharacteristic
from ...utils.helper_methods import get_virtual_box_vminfo

log = logging.getLogger()


def serial_randomize(start=0, string_length=10):
    rand = str(uuid.uuid4())
    rand = rand.upper()
    rand = re.sub('-', '', rand)
    return rand[start:string_length]


def _modify_first_nic_mac_address(random_mac, vm_name):
    subprocess.run(
        ["VBoxManage", "modifyvm", vm_name, "--macaddress1", random_mac],
        check=True,
    )


class MacAddressCharacteristic(PreBootCharacteristic):
    """Checks and Fixes the mac-address of the Vagrant NIC."""

    def __init__(self):
        super().__init__("MACVB1", "Randomize mac-address of vagrant NIC.")

    def fix(self) -> CheckResult:
        vm_name = self.environment.vm_name
        random_mac = "98e743%02x%02x%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        if vm_name:
            _modify_first_nic_mac_address(random_mac, vm_name)
        return self.check()

    def check(self) -> CheckResult:
        """Checks if `macaddress1` starts with 080027 (vbox prefix)."""
        vm_name = self.environment.vm_name
        is_fixed: bool = True
        if vm_name:
            result = get_virtual_box_vminfo(vm_name)
            for entry in result.stdout.decode("utf-8").split("\n"):
                if 'macaddress1="080027' in entry:
                    is_fixed = False
        yield self, CheckType(self.description, is_fixed)
