"""This module contains a class for adding dmi hardware characteristics from the host to the VM."""
import logging
import subprocess
import sys
from pathlib import Path

from ..abstract_characteristic import (CheckResult, CheckType, PreBootCharacteristic, Characteristic)
from ...utils.helper_methods import get_config_root, get_project_root, run_external_program_no_return
from ...utils.windows_devices import remove_windows_devices_by_wildcard, str_exists_in_wmi_queries_results

log = logging.getLogger()
TARGET_SCRIPT_DIR = get_config_root() / "data"
DATA_DIR = Path(get_project_root() / "data/")


class DMIHardwareCharacteristic(PreBootCharacteristic):
    """Checks and Fixes cpuid hypervisor bit in Virtualbox."""

    def __init__(self):
        super().__init__("HWDMI", "DMI Hardware properties from host system.")

    def fix(self) -> CheckResult:
        vm_name = self.environment.vm_name
        hardware_script_generation_script = str(Path(__file__).parent / "generate_hardware_shell_script.py")
        if not (TARGET_SCRIPT_DIR / "hardware_fix_script.sh").is_file():
            print("[!] Sudo access needed to create hardware_shell_script")
            subprocess.call(
                ["sudo", sys.executable, hardware_script_generation_script, str(TARGET_SCRIPT_DIR),
                 str(DATA_DIR)])
        run_external_program_no_return("bash", str(TARGET_SCRIPT_DIR / "hardware_fix_script.sh"), vm_name)
        return self.check()

    def check(self) -> CheckResult:
        """Checks if dmi hardware modification were executed."""
        vm_name = self.environment.vm_name
        if vm_name:
            log.debug(f"Run VBoxManage getextradata {vm_name} enumerate.")
            result = subprocess.run(
                ["VBoxManage", "getextradata", vm_name, "enumerate"],
                stdout=subprocess.PIPE,
                check=True,
            )
            self.is_fixed = len(result.stdout.decode("utf-8").split("\n")) > 3
        yield self, CheckType(self.description, self.is_fixed)


class VBoxDeviceRemoval(Characteristic):
    """Removes devices such as disks named *VBOX* with DevManView.exe."""

    def __init__(self) -> None:
        super().__init__("VBDev", "VirtualBox devices named *VBOX*")

    def fix(self) -> CheckResult:
        remove_windows_devices_by_wildcard("VBOX")
        return self.check()

    def check(self) -> CheckResult:
        query_disk_drive = "SELECT * FROM win32_diskdrive"
        vbox_dev_exists = str_exists_in_wmi_queries_results("VBOX", query_disk_drive)
        if vbox_dev_exists is True:
            yield self, CheckType(self.description, True)
            return
        if vbox_dev_exists is None:
            yield self, CheckType("Skipped, malvm is not running on Windows.", False)
            return
        yield self, CheckType(self.description, False)
