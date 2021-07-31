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


def str_to_bool(boolean_str: str) -> bool:
    return boolean_str.lower() in ("yes", "true", "t", "1")


class DSDTRegistry(Characteristic):
    """Fixes DSDT entries in the registry."""

    def __init__(self) -> None:
        super().__init__("DSDT", "Fixes DSDT entries in the registry.")

    def fix(self) -> CheckResult:
        command_copy = r"Copy-Item -Path HKLM:\HARDWARE\ACPI\DSDT\VBOX__ " \
                       r"-Destination HKLM:\HARDWARE\ACPI\DSDT\DELL__ -Recurse;" \
                       r"Copy-Item -Path HKLM:\HARDWARE\ACPI\DSDT\DELL__\VBOXBIOS " \
                       r"-Destination HKLM:\HARDWARE\ACPI\DSDT\DELL__\CBX3___ -Recurse;" \
                       r"Copy-Item -Path HKLM:\HARDWARE\ACPI\DSDT\DELL__\CBX3___\00000002 " \
                       r"-Destination HKLM:\HARDWARE\ACPI\DSDT\DELL__\CBX3___\01072009 -Recurse"

        command_remove = r"Remove-Item -Path HKLM:\HARDWARE\ACPI\DSDT\VBOX__ -Recurse; " \
                         r"Remove-Item -Path HKLM:\HARDWARE\ACPI\DSDT\DELL__\VBOXBIOS -Recurse; " \
                         r"Remove-Item -Path HKLM:\HARDWARE\ACPI\DSDT\DELL__\CBX3___\00000002 -Recurse"
        subprocess.run(["powershell", "-Command", command_copy], check=False)
        subprocess.run(["powershell", "-Command", command_remove], check=False)

        return self.check()

    def check(self) -> CheckResult:
        result_bool_one = str_to_bool(subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\DSDT\VBOX__'"))
        result_bool_two = str_to_bool(
            subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\DSDT\DELL__\VBOXBIOS'"))
        result_bool_three = str_to_bool(
            subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\DSDT\DELL__\CBX3___\00000002'"))
        result_bool_four = str_to_bool(subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\DSDT\DELL__'"))
        result_bool_five = str_to_bool(
            subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\DSDT\DELL__\CBX3___'"))
        result_bool_six = str_to_bool(
            subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\DSDT\DELL__\CBX3___\01072009'"))
        yield self, CheckType(self.description,
                              all([not result_bool_one, not result_bool_two, not result_bool_three, result_bool_four,
                                   result_bool_five, result_bool_six]))


class FADTRegistry(Characteristic):
    """Fixes FADT entries in the registry."""

    def __init__(self) -> None:
        super().__init__("FADT", "Fixes FADT entries in the registry.")

    def fix(self) -> CheckResult:
        command = r"$version = (Get-WmiObject win32_operatingsystem).version;" \
                  r"if ($version -like '10.0*') {" \
                  r"$oddity = 'HKLM:\HARDWARE\ACPI\FADT\' + " \
                  r"(Get-ChildItem 'HKLM:\HARDWARE\ACPI\FADT' -Name);" \
                  r"if ($oddity -ne 'HKLM:\HARDWARE\ACPI\FADT\DELL') {" \
                  r"Invoke-Expression ('Copy-Item -Path ' + $oddity + " \
                  r"' -Destination HKLM:\HARDWARE\ACPI\FADT\DELL -Recurse');" \
                  r"Invoke-Expression ('Remove-Item -Path ' + $oddity + ' -Recurse')};" \
                  r"Copy-Item -Path HKLM:\HARDWARE\ACPI\FADT\DELL\VBOXFACP " \
                  r"-Destination HKLM:\HARDWARE\ACPI\FADT\DELL\CBX3___ -Recurse;" \
                  r"Remove-Item -Path HKLM:\HARDWARE\ACPI\FADT\*\VBOXFACP -Recurse;" \
                  r"Copy-Item -Path HKLM:\HARDWARE\ACPI\FADT\DELL\CBX3___\00000001 " \
                  r"-Destination HKLM:\HARDWARE\ACPI\FADT\DELL\CBX3___\01072009 -Recurse;" \
                  r"Remove-Item -Path HKLM:\HARDWARE\ACPI\FADT\*\CBX3___\\00000001 -Recurse;}"

        subprocess.run(["powershell", "-Command", command], check=False)

        return self.check()

    def check(self) -> CheckResult:
        result_bool_one = str_to_bool(
            subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\FADT\*\VBOXFACP'"))
        result_bool_two = str_to_bool(
            subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\FADT\*\CBX3___\\00000001'"))
        result_bool_three = str_to_bool(subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\FADT\DELL'"))
        result_bool_four = str_to_bool(
            subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\FADT\DELL\CBX3___'"))
        result_bool_five = str_to_bool(
            subprocess.getoutput(r"powershell Test-Path 'HKLM:\HARDWARE\ACPI\FADT\DELL\CBX3___\01072009'"))
        yield self, CheckType(self.description,
                              all([not result_bool_one, not result_bool_two, result_bool_three,
                                   result_bool_four, result_bool_five]))
