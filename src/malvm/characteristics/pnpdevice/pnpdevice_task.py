"""This module contains a class for removing plug and play devices connected to VirtualBox.

Classes:
    PnPDeviceCharacteristic: Removes plug and play devices named *DEV_CAFE* with DevManView.exe.
"""
import logging

from ..abstract_characteristic import Characteristic, CheckResult, CheckType
from ...utils.windows_devices import remove_windows_devices_by_wildcard, str_exists_in_wmi_queries_results

log = logging.getLogger()


class PnPDeviceCharacteristic(Characteristic):
    """Removes plug and play devices named *DEV_CAFE* with DevManView.exe."""

    def __init__(self) -> None:
        super().__init__("PnPDev", "PnPDevices named *DEV_CAFE*")

    def fix(self) -> CheckResult:
        remove_windows_devices_by_wildcard("DEV_CAFE")
        return self.check()

    def check(self) -> CheckResult:
        query_pnpdevice = "SELECT * FROM win32_pnpdevice"
        query_pnpentity = "SELECT * FROM Win32_PnPEntity"
        pnp_dev_exists = str_exists_in_wmi_queries_results("DEV_CAFE", query_pnpdevice, query_pnpentity)
        if pnp_dev_exists is True:
            yield self, CheckType(self.description, True)
            return
        if pnp_dev_exists is None:
            yield self, CheckType("Skipped, malvm is not running on Windows.", False)
            return
        yield self, CheckType(self.description, False)
