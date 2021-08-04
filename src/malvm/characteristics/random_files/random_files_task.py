"""This module contains classes for characteristics of RandomFiles.

Classes:
    RandomFiles: Generates random files.
"""
import subprocess
from pathlib import Path

from ..abstract_characteristic import Characteristic, CheckResult, CheckType


class RandomFiles(Characteristic):
    """Generates random files."""

    def __init__(self) -> None:
        super().__init__("RNDF", "Generates random files.")

    def fix(self) -> CheckResult:
        # pylint: disable=anomalous-backslash-in-string
        task = """
# RandomDate function\r\n
function RandomDate {\r\n
  $days = Get-Random -minimum 300 -maximum 2190\r\n
  $hours = Get-Random -minimum 5 -maximum 24\r\n
  $minutes = Get-Random -minimum 20 -maximum 60\r\n
  $seconds = Get-Random -minimum 12 -maximum 60\r\n
  return $days,$hours,$minutes,$seconds\r\n
}\r\n
# Generate files\r\n
function GenFiles([string]$status) {\r\n
 $TimeStamp = RandomDate\r\n
 $ext = Get-Random -input ".pdf",".txt",".docx",".doc",".xls", ".xlsx",".zip",".png",".jpg", ".jpeg", ".gif", ".bmp", ".html", ".htm", ".ppt", ".pptx"\r\n
 $namely = Get-Random -input "wichtig", "Secret", "do_not_share", "experimental", "meeting", "magic"\r\n
 if ($version -notlike '10.0*') {\r\n
  $location = Get-Random -input "$ENV:userprofile\Desktop\\", "$ENV:userprofile\Documents\\", "$ENV:homedrive\\", "$ENV:userprofile\Downloads\\", "$ENV:userprofile\Pictures\\"\r\n
 } else {\r\n
  $location = Get-Random -input "$ENV:userprofile\Desktop\\", "$ENV:userprofile\Documents\\", "$ENV:userprofile\Downloads\\", "$ENV:userprofile\Pictures\\"\r\n
 }\r\n
 $length = Get-Random -minimum 300 -maximum 4534350\r\n
 $buffer = New-Object Byte[] $length\r\n
 New-Item $location$namely$ext -type file -value $buffer\r\n
 Get-ChildItem $location$namely$ext | % {$_.CreationTime = ((get-date).AddDays(-$TimeStamp[0]).AddHours(-$TimeStamp[1]).AddMinutes(-$TimeStamp[2]).AddSeconds(-$TimeStamp[3])) }\r\n
 Get-ChildItem $location$namely$ext | % {$_.LastWriteTime = ((get-date).AddDays(-$TimeStamp[0]).AddHours(-$TimeStamp[1]).AddMinutes(-$TimeStamp[2]).AddSeconds(-$TimeStamp[3])) }\r\n
 if ($status -eq "delete"){\r\n
  # Now thrown them away!\r\n
  $shell = new-object -comobject "Shell.Application"\r\n
  $item = $shell.Namespace(0).ParseName("$location$namely$ext")\r\n
  $item.InvokeVerb("delete")\r\n
  }\r\n
}\r\n
# Generate files and then throw them away\r\n
$amount = Get-Random -minimum 10 -maximum 30\r\n
for ($x=0; $x -le $amount; $x++) {\r\n
  GenFiles delete\r\n
}\r\n
# Generate files, but these we keep\r\n
$amount = Get-Random -minimum 15 -maximum 45\r\n
for ($x=0; $x -le $amount; $x++) {\r\n
  GenFiles\r\n
}
        """  # noqa: E501,W605
        tmp_script_path = Path("tmp_script.ps1")
        with tmp_script_path.open(mode="w") as file_descriptor:
            file_descriptor.write(task)
        subprocess.run(["powershell", tmp_script_path.name], check=False)
        tmp_script_path.unlink()
        return self.check()

    def check(self) -> CheckResult:
        result = subprocess.getoutput(
            r"powershell (Get-Childitem –Path C:\Users\ -Include *.HTML,*.PDF,*.WAV -File -Recurse)")
        yield self, CheckType(self.description, all([result]))
