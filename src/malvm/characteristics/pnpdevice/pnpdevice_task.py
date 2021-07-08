"""This module contains a class for removing plug and play devices connected to VirtualBox.

Classes:
    PnPDeviceCharacteristic: Removes plug and play devices named *DEV_CAFE* with DevManView.exe.
"""
import logging
import subprocess
import sys

from ..abstract_characteristic import Characteristic, CheckResult, CheckType
from ...utils.helper_methods import get_data_dir

log = logging.getLogger()


class PnPDeviceCharacteristic(Characteristic):
    """Removes plug and play devices named *DEV_CAFE* with DevManView.exe."""

    def __init__(self) -> None:
        super().__init__("PnPDev", "PnPDevices named *DEV_CAFE*")

    def fix(self) -> CheckResult:
        dev_man_view_path = get_data_dir() / "DevManView.exe"
        if dev_man_view_path.is_file():
            subprocess.Popen([f'{str(dev_man_view_path.absolute())}', '/uninstall "*DEV_CAFE*" / use_wildcard'])
        else:
            log.error(f"Path {dev_man_view_path.absolute()} does not exist.")
            raise FileNotFoundError(f"File {dev_man_view_path.absolute()} was not found.")
        return self.check()

    def check(self) -> CheckResult:
        # pylint: disable=import-outside-toplevel
        if sys.platform == 'win32':
            import wmi
            wmi_interface = wmi.WMI()
            query_pnpdevice = "SELECT * FROM win32_pnpdevice"
            query_pnpentity = "SELECT * FROM Win32_PnPEntity"
            for result in wmi_interface.query(query_pnpdevice):
                if "DEV_CAFE" in str(result):
                    yield self, CheckType(self.description, False)
            for result in wmi_interface.query(query_pnpentity):
                if "DEV_CAFE" in str(result):
                    yield self, CheckType(self.description, False)
            yield self, CheckType(self.description, True)
            return
        yield self, CheckType("Skipped, malvm is not running on Windows.", False)
