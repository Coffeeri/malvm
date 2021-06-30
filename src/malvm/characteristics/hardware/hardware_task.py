import logging
import subprocess
import sys
from pathlib import Path

from ..abstract_characteristic import (CheckResult, CheckType, PreBootCharacteristic)
from ...utils.helper_methods import get_config_root, get_project_root

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
        subprocess.run(["bash", str(TARGET_SCRIPT_DIR / "hardware_fix_script.sh"), vm_name], check=True)
        return self.check()

    def check(self) -> CheckResult:
        """Checks if dmi hardware modification were executed."""
        vm_name = self.environment.vm_name
        is_fixed: bool = False
        if vm_name:
            log.debug(f"Run VBoxManage getextradata {vm_name} enumerate.")
            result = subprocess.run(
                ["VBoxManage", "getextradata", vm_name, "enumerate"],
                stdout=subprocess.PIPE,
                check=True,
            )
            is_fixed = len(result.stdout.decode("utf-8").split("\n")) > 3
        yield self, CheckType(self.description, is_fixed)