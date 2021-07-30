"""This module contains classes for characteristics of OS install date.

Classes:
    OSInstallDate: Changes the os install date to an older one.
"""
import subprocess
import time

from ..abstract_characteristic import Characteristic, CheckResult, CheckType
from ..registry.registry_task import check_registry_key_value, RegistryTask, RegistryAction


def calc_ptime():
    format = '%m/%d/%Y %I:%M %p'
    start = "8/6/2018 5:30 PM"
    end = time.strftime("%m/%d/%Y %I:%M %p")
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    return stime + 0.05 * (etime - stime)


class OSInstallDate(Characteristic):
    """Changes the os install date to an older one."""

    def __init__(self) -> None:
        super().__init__("OSD", "Sets the OS install date.")

    def fix(self) -> CheckResult:
        ptime = calc_ptime()

        command_task_cur_vers = f"New-ItemProperty " \
                                f"-Path \"HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\" " \
                                f"-Name \"InstallDate\" " \
                                f"-Value \"{hex(int(ptime))}\" " \
                                f"-PropertyType \"DWord\" " \
                                f"-force"

        command_task_iexplorer_date = f"New-ItemProperty " \
                                      f"-Path \"HKCU:\SOFTWARE\Microsoft\Internet Explorer\SQM\" " \
                                      f"-Name \"InstallDate\" " \
                                      f"-Value \"{hex(int(ptime))}\" " \
                                      f"-PropertyType \"DWord\" " \
                                      f"-force"

        print(command_task_cur_vers)
        print(command_task_iexplorer_date)
        subprocess.run(["powershell", "-Command", command_task_cur_vers])
        subprocess.run(["powershell", "-Command", command_task_iexplorer_date])
        return self.check()

    def check(self) -> CheckResult:
        ptime = calc_ptime()
        task_cur_vers = RegistryTask(slug="CURVERS",
                                     action=RegistryAction.CHANGE,
                                     hypervisor="VBOX",
                                     key="HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                                     parameter="InstallDate",
                                     value=str(hex(int(ptime)))
                                     )
        task_iexplorer_date = RegistryTask(slug="CURVERS",
                                           action=RegistryAction.CHANGE,
                                           hypervisor="VBOX",
                                           key="HKCU:\SOFTWARE\Microsoft\Internet Explorer\SQM",
                                           parameter="InstallDate",
                                           value=str(hex(int(ptime)))
                                           )
        result_cur_vers = check_registry_key_value(task_cur_vers)
        result_iexplorer_date = check_registry_key_value(task_iexplorer_date)
        yield self, CheckType(self.description, all([result_cur_vers, result_iexplorer_date]))
