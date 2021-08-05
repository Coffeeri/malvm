"""This module contains classes for characteristics of ProductID.

Classes:
    ProductID: Randomize Windows-Product-ID.
"""
import random
import subprocess
from pathlib import Path

from ..abstract_characteristic import Characteristic, CheckResult, CheckType
from ..registry.registry_task import RegistryTask, RegistryAction, check_registry_key_value


class ProductID(Characteristic):
    """Randomize Windows-Product-ID."""

    def __init__(self) -> None:
        super().__init__("WINID", "Randomize Windows-Product-ID.")
        serial_block_length = [5, 3, 7, 5]
        blocks = []
        for block_length in serial_block_length:
            new_block = "".join([str(random.randint(0, 9)) for _ in range(0, block_length)])
            blocks.append(new_block)
        self.new_product_id = "-".join(blocks)

    def fix(self) -> CheckResult:
        # pylint: disable=anomalous-backslash-in-string
        task_one = f"""
New-ItemProperty -Path \"HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\" -Name ProductId -Value "{self.new_product_id}" -PropertyType "String" -force
New-ItemProperty -Path \"HKLM:\SOFTWARE\Microsoft\Internet Explorer\Registration\" -Name ProductId -Value "{self.new_product_id}" -PropertyType "String" -force
New-ItemProperty -Path \"HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\DefaultProductKey\" -Name ProductId -Value "{self.new_product_id}" -PropertyType "String" -force
# Clear the Product key from the registry (prevents people from stealing it)
$slmgr="cscript $ENV:windir\system32\slmgr.vbs /cpky"
iex $slmgr
$newProductId = "{self.new_product_id}"
        """  # noqa: E501,W605

        task_two = """
$newProductId = $newProductId.ToCharArray()
$convert = ""
foreach ($x in $newProductId) {
 $convert += $x -as [int]
}
$newNewProductId = $convert -split "(..)" | ? { $_ }
$convertID = @()
foreach ($x in $newNewProductId) {
 $convertID += [Convert]::ToString($x,16)
}
$data = (Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\DefaultProductKey" -Name DigitalProductId).DigitalProductId
$convertData = ""
foreach ($x in $data) {
 $convertData += [Convert]::ToString($x,16)
}
$con1 = $convertData.Substring(0,62)
$con2 = $convertData.Substring(62)
$con2 = $con2 -split "(..)" | ? { $_}
$static = @("A4","00","00","00","03","00","00","00")
# Finalize
$hexDigitalProductId = $static + $convertID + $con2
$hexHexDigitalProductId = @()
foreach ($xxx in $hexDigitalProductId) {
   $hexHexDigitalProductId += "0x$xxx"
}
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion" -Name DigitalProductId  -Value ([byte[]] $hexHexDigitalProductId)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Internet Explorer\Registration" -Name DigitalProductId  -Value ([byte[]] $hexHexDigitalProductId)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\DefaultProductKey" -Name DigitalProductId  -Value ([byte[]] $hexHexDigitalProductId)
        """  # noqa: E501,W605
        tmp_script_path = Path("tmp_script.ps1")
        with tmp_script_path.open(mode="w") as file_descriptor:
            file_descriptor.write(task_one)
            file_descriptor.write(task_two)
        subprocess.run(["powershell", tmp_script_path.name], check=False)
        tmp_script_path.unlink()
        return self.check()

    def check(self) -> CheckResult:
        win_nt_cur_vers = RegistryTask(slug="CURVERS",
                                       action=RegistryAction.CHANGE,
                                       hypervisor="VBOX",
                                       key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                                       parameter="ProductId",
                                       value=self.new_product_id
                                       )
        iex_registration = RegistryTask(slug="CURVERS",
                                        action=RegistryAction.CHANGE,
                                        hypervisor="VBOX",
                                        key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer\Registration",
                                        parameter="ProductId",
                                        value=self.new_product_id
                                        )
        default_product_key = RegistryTask(slug="CURVERS",
                                           action=RegistryAction.CHANGE,
                                           hypervisor="VBOX",
                                           key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows "
                                               r"NT\CurrentVersion\DefaultProductKey",
                                           parameter="ProductId",
                                           value=self.new_product_id
                                           )
        result_win_nt_cur_vers = check_registry_key_value(win_nt_cur_vers)
        result_iex_registration = check_registry_key_value(iex_registration)
        result_default_product_key = check_registry_key_value(default_product_key)
        yield self, CheckType(self.description,
                              all([result_win_nt_cur_vers, result_iex_registration, result_default_product_key]))
