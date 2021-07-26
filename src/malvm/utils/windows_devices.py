"""This module contains helper methods for handling windows devices"""
import logging
import subprocess
import sys
from typing import Optional

from .helper_methods import get_data_dir

log = logging.getLogger()


def remove_windows_devices_by_wildcard(pattern: str):
    dev_man_view_path = get_data_dir() / "DevManView.exe"
    if dev_man_view_path.is_file():
        subprocess.Popen([f'{str(dev_man_view_path.absolute())}', f'/uninstall "*{pattern}*" /use_wildcard'])
    else:
        log.error(f"Path {dev_man_view_path.absolute()} does not exist.")
        raise FileNotFoundError(f"File {dev_man_view_path.absolute()} was not found.")


def str_exists_in_wmi_queries_results(search_str: str, *wmi_queries: str) -> Optional[bool]:
    # pylint: disable=import-outside-toplevel
    if sys.platform != 'win32':
        return None
    import wmi  # type: ignore
    wmi_interface = wmi.WMI()
    for query in wmi_queries:
        for result in wmi_interface.query(query):
            if search_str in str(result):
                return False
    return True
