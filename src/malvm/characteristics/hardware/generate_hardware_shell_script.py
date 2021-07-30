"""This module is used to create a hardware modifier script.

This python script need to run as root, to obtain dmi information.

"""
# credits to https://github.com/nsmfoo/antivmdetection/blob/master/antivmdetect.py and
# https://github.com/Cisco-Talos/vboxhardening/
# https://github.com/hfiref0x/VBoxHardenedLoader/ Copyright (c) 2014 - 2020, VBoxHardenedLoader authors
# pylint: skip-file
import argparse
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

from dmidecode import DMIDecode  # type: ignore


def serial_randomize(start=0, string_length=10):
    rand = str(uuid.uuid4())
    rand = rand.upper()
    rand = re.sub('-', '', rand)
    return rand[start:string_length]


parser = argparse.ArgumentParser(description='Generate hardware configuration script.')

parser.add_argument('dest',
                    type=str,
                    help='Destination path of shell script.')
parser.add_argument('data_path',
                    type=str,
                    help='Source path of files such as DSDT_SLIC.bin.')

args = parser.parse_args()
if not Path(args.dest).is_dir() or not Path(args.data_path).is_dir():
    sys.exit(1)

HARDWARE_FIX_SHELL_SCRIPT = str(args.dest + "/hardware_fix_script.sh")
DSDT_FILE = str(args.data_path + "/DSDT_SLIC.bin")
ACPI_DSDT_FILE = str(args.data_path + "/ACPI-DSDT-new.bin")
ACPI_SSDT_FILE = str(args.data_path + "/ACPI-SSDT1-new.bin")
VIDEO_FILE = str(args.data_path + "/vgabios386.bin")
PCBIOS_FILE = str(args.data_path + "/pcbios386.bin")
PXE_FILE = str(args.data_path + "/pxerom.bin")

if os.geteuid() != 0:
    print("Script need root access.")
    subprocess.call(['sudo', 'python3', *sys.argv])
    sys.exit(1)

dmi = DMIDecode()
dmi_info = {}

try:
    for v in dmi.get(0):
        if type(v) == dict and v['DMIType'] == 0:
            dmi_info['DmiBIOSVendor'] = "string:" + v['Vendor']
            dmi_info['DmiBIOSVersion'] = "string:" + v['Version'].replace(" ", "")
            biosversion = v['BIOS Revision']
            dmi_info['DmiBIOSReleaseDate'] = "string:" + v['Release Date']
except Exception:
    # This typo is deliberate, as a previous version of py-dmidecode contained a typo
    dmi_info['DmiBIOSReleaseDate'] = "string:" + v['Relase Date']

try:
    dmi_info['DmiBIOSReleaseMajor'], dmi_info['DmiBIOSReleaseMinor'] = biosversion.split('.', 1)
except Exception:
    dmi_info['DmiBIOSReleaseMajor'] = '** No value to retrieve **'
    dmi_info['DmiBIOSReleaseMinor'] = '** No value to retrieve **'

# python-dmidecode does not currently reveal all values .. this is plan B
dmi_firmware = subprocess.getoutput("dmidecode t0")
try:
    dmi_info['DmiBIOSFirmwareMajor'], dmi_info['DmiBIOSFirmwareMinor'] = re.search(  # type: ignore
        "Firmware Revision: ([0-9A-Za-z. ]*)", dmi_firmware).group(1).split('.', 1)

except Exception:
    dmi_info['DmiBIOSFirmwareMajor'] = '** No value to retrieve **'
    dmi_info['DmiBIOSFirmwareMinor'] = '** No value to retrieve **'

for v in dmi.get(2):
    if type(v) == dict and v['DMIType'] == 2:
        serial_number = v['Serial Number']
        dmi_info['DmiBoardVersion'] = "string:" + v['Version'].replace(" ", "")
        dmi_info['DmiBoardProduct'] = "string:" + v['Product Name'].replace(" ", "")
        dmi_info['DmiBoardVendor'] = "string:" + v['Manufacturer'].replace(" ", "")

# This is hopefully not the best solution ..
try:
    s_number = []
    if serial_number:
        # Get position
        if '/' in serial_number:
            for slash in re.finditer('/', serial_number):
                s_number.append(slash.start(0))
                # Remove / from string
                new_serial = re.sub('/', '', serial_number)
                new_serial = serial_randomize(0, len(new_serial))
            # Add / again
            for char in s_number:
                new_serial = new_serial[:char] + '/' + new_serial[char:]
        else:
            new_serial = serial_randomize(0, len(serial_number))
    else:
        new_serial = "** No value to retrieve **"
except Exception:
    new_serial = "** No value to retrieve **"

dmi_info['DmiBoardSerial'] = new_serial

# python-dmidecode does not reveal all values .. this is plan B
dmi_board = subprocess.getoutput("dmidecode -t2")
try:
    asset_tag = re.search("Asset Tag: ([0-9A-Za-z ]*)", dmi_board).group(1)  # type: ignore

except Exception:
    asset_tag = '** No value to retrieve **'

dmi_info['DmiBoardAssetTag'] = "string:" + asset_tag

try:
    loc_chassis = re.search("Location In Chassis: ([0-9A-Za-z ]*)", dmi_board).group(1)  # type: ignore
except Exception:
    loc_chassis = '** No value to retrieve **'

dmi_info['DmiBoardLocInChass'] = "string:" + loc_chassis.replace(" ", "")

# Based on the list from https://www.dmtf.org/sites/default/files/standards/documents/DSP0134_3.4.0.pdf
board_dict = {'Unknown': 1, 'Other': 2, 'Server Blade': 3, 'Connectivity Switch': 4, 'System Management Module': 5,
              'Processor Module': 6, 'I/O Module': 7, 'Memory Module': 8, 'Daughter board': 9, 'Motherboard': 10,
              'Processor/Memory Module': 11, 'Processor/IO Module': 12, 'Interconnect board': 13}
try:
    board_type = re.search("Type: ([0-9A-Za-z ]+)", dmi_board).group(1)  # type: ignore
    board_type = str(board_dict.get(board_type))
except Exception:
    board_type = '** No value to retrieve **'

dmi_info['DmiBoardBoardType'] = board_type

for v in dmi.get(1):
    if type(v) == dict and v['DMIType'] == 1:
        dmi_info['DmiSystemSKU'] = "string:" + v['SKU Number']
        system_family = v['Family']
        system_serial = v['Serial Number']
        dmi_info['DmiSystemVersion'] = "string:" + v['Version'].replace(" ", "")
        dmi_info['DmiSystemProduct'] = "string:" + v['Product Name'].replace(" ", "")
        dmi_info['DmiSystemVendor'] = "string:" + v['Manufacturer'].replace(" ", "")

if not system_family:
    dmi_info['DmiSystemFamily'] = "Not Specified"
else:
    dmi_info['DmiSystemFamily'] = "string:" + system_family

# Create a new UUID
newuuid = str(uuid.uuid4())
dmi_info['DmiSystemUuid'] = newuuid.upper()
# Create a new system serial number
dmi_info['DmiSystemSerial'] = "string:" + (serial_randomize(0, len(system_serial)))

for v in dmi.get(3):
    dmi_info['DmiChassisVendor'] = "string:" + v['Manufacturer'].replace(" ", "")
    chassi_serial = v['Serial Number']
    dmi_info['DmiChassisVersion'] = "string:" + v['Version'].replace(" ", "")
    dmi_info['DmiChassisType'] = v['Type']

# Based on the list from https://www.dmtf.org/sites/default/files/standards/documents/DSP0134_3.4.0.pdf
chassi_dict = {'Other': 1, 'Unknown': 2, 'Desktop': 3, 'Low Profile Desktop': 4, 'Pizza Box': 5, 'Mini Tower': 6,
               'Tower': 7, 'Portable': 8, 'Laptop': 9, 'Notebook': 10, 'Hand Held': 11, 'Docking Station': 12,
               'All in One': 13, 'Sub Notebook': 14, 'Space-saving': 15, 'Lunch Box': 16, 'Main Server Chassis': 17,
               'Expansion Chassis': 18, 'SubChassis': 19, 'Bus Expansion Chassis': 20, 'Peripheral Chassis': 21,
               'RAID Chassis': 22,
               'Rack Mount Chassis': 23, 'Sealed-case PC': 24, 'Multi-system chassis': 25, 'Compact PCI': 26,
               'Advanced TCA': 27,
               'Blade': 28, 'Blade Enclosure': 29, 'Tablet': 30, 'Convertible': 31, 'Detachable': 32,
               'IoT Gateway': 33,
               'Embedded PC': 34, 'Mini PC': 35, 'Stick PC': 36}

dmi_info['DmiChassisType'] = str(chassi_dict.get(dmi_info['DmiChassisType']))

# python-dmidecode does not reveal all values .. this is plan B
chassi = subprocess.getoutput("dmidecode -t3")
try:
    dmi_info['DmiChassisAssetTag'] = "string:" + re.search("Asset Tag: ([0-9A-Za-z ]*)", chassi).group(  # type: ignore
        1)
except Exception:
    dmi_info['DmiChassisAssetTag'] = '** No value to retrieve **'

# Create a new chassi serial number
dmi_info['DmiChassisSerial'] = "string:" + (serial_randomize(0, len(chassi_serial)))

for v in dmi.get(4):
    dmi_info['DmiProcVersion'] = "string:" + v['Version'].replace(" ", "")
    dmi_info['DmiProcManufacturer'] = "string:" + v['Manufacturer'].replace(" ", "")
# OEM strings

try:
    for v in dmi.get(11):
        oem_ver = v['Strings']['3']
        oem_rev = v['Strings']['2']
except Exception:
    pass
try:
    dmi_info['DmiOEMVBoxVer'] = "string:" + oem_ver
    dmi_info['DmiOEMVBoxRev'] = "string:" + oem_rev
except Exception:
    dmi_info['DmiOEMVBoxVer'] = '** No value to retrieve **'
    dmi_info['DmiOEMVBoxRev'] = '** No value to retrieve **'

logfile = open(HARDWARE_FIX_SHELL_SCRIPT, 'w+')
logfile.write('#Script generated on: ' + time.strftime("%H:%M:%S") + '\n')
bash = """ if [ $# -eq 0 ]
  then
    echo "[*] Please add vm name!"
    echo "[*] Available vms:"
    VBoxManage list vms | awk -F'"' {' print $2 '} | sed 's/"//g'
    exit
fi """
logfile.write(bash + '\n')

for k, v in sorted(dmi_info.items()):
    if '** No value to retrieve **' in v:
        logfile.write('# VBoxManage setextradata "$1" VBoxInternal/Devices/pcbios/0/Config/' + k + '\t' + v + '\n')
    else:
        logfile.write(
            'VBoxManage setextradata "$1" VBoxInternal/Devices/pcbios/0/Config/' + k + '\t\'' + v + '\'\n')
# Disk information
disk_dmi = {}
disk_name = subprocess.getoutput("df -P / | tail -n 1 | awk '/.*/ { print $1 }'")

# Handle Ubuntu live-cd
if '/cow' in disk_name:
    disk_name = "/dev/sdb"

# Disk serial
try:
    if Path(disk_name).exists():
        disk_serial = subprocess.getoutput(
            "smartctl -i " + disk_name + r" | grep -o 'Serial Number:  [A-Za-z0-9_\+\/ .\"-]*' | awk '{print $3}'")
        if 'SG_IO' in disk_serial or not disk_serial:
            print(
                '[WARNING] Unable to acquire the disk serial number! Will add one, but please try to run this script '
                'on another machine instead..')
            disk_serial = 'HUA721010KLA330'

        disk_dmi['SerialNumber'] = (serial_randomize(0, len(disk_serial)))

        if len(disk_dmi['SerialNumber']) > 20:
            disk_dmi['SerialNumber'] = disk_dmi['SerialNumber'][:20]
except OSError:
    print('Error reading system disk..')

# Disk firmware rev
try:
    if Path(disk_name).exists():
        disk_fwrev = subprocess.getoutput(
            "smartctl -i " + disk_name + r" | grep -o 'Firmware Version: [A-Za-z0-9_\+\/ .\"-]*' | awk '{print $3}'")
        disk_dmi['FirmwareRevision'] = "string:" + disk_fwrev
        if 'SG_IO' in disk_dmi['FirmwareRevision']:
            print(
                '[WARNING] Unable to acquire the disk firmware revision! Will add one, but please try to run this '
                'script on another machine instead..')
            disk_dmi['FirmwareRevision'] = 'LMP07L3Q'
            disk_dmi['FirmwareRevision'] = "string:" + (serial_randomize(0, len(disk_dmi['FirmwareRevision'])))
except OSError:
    print('Error reading system disk..')

# Disk model number
try:
    if Path(disk_name).exists():
        disk_modelno = subprocess.getoutput(
            "smartctl -i " + disk_name + r" | grep -o 'Model Family: [A-Za-z0-9_\+\/ .\"-]*' | awk '{print $3}'")
        disk_dmi['ModelNumber'] = disk_modelno

        if 'SG_IO' in disk_dmi['ModelNumber'] or not disk_modelno:
            print(
                '[WARNING] Unable to acquire the disk model number! Will add one, but please try to run this script '
                'on another machine instead..')
            disk_vendor = 'SAMSUNG'
            disk_vendor_part1 = 'F8E36628D278'
            disk_vendor_part1 = (serial_randomize(0, len(disk_vendor_part1)))
            disk_vendor_part2 = '611D3'
            disk_vendor_part2 = (serial_randomize(0, len(disk_vendor_part2)))
            disk_dmi['ModelNumber'] = (serial_randomize(0, len(disk_dmi['ModelNumber'])))
            disk_dmi['ModelNumber'] = disk_vendor + ' ' + disk_vendor_part1 + '-' + disk_vendor_part2
except OSError:
    print('Error reading system disk..')

logfile.write('controller=`VBoxManage showvminfo "$1" --machinereadable | grep SATA`\n')

logfile.write('if [[ -z "$controller" ]]; then\n')
for k, v in disk_dmi.items():
    if '** No value to retrieve **' in v:
        logfile.write(
            '# VBoxManage setextradata "$1" '
            'VBoxInternal/Devices/piix3ide/0/Config/PrimaryMaster/' + k + '\t' + v + '\n')
    else:
        logfile.write(
            'VBoxManage setextradata "$1" '
            'VBoxInternal/Devices/piix3ide/0/Config/PrimaryMaster/' + k + '\t\'' + v + '\'\n')

# CD-Drive
# logfile.write(
# 'VBoxManage setextradata "$1" "VBoxInternal/Devices/piix3ide/0/Config/Port1/ModelNumber" "HL-DT-ST DVDRAM GUE2P"\t\n')
# logfile.write('VBoxManage setextradata "$1"
# "VBoxInternal/Devices/piix3ide/0/Config/Port1/FirmwareRevision" "AS01"\t\n')
# logfile.write(
#     'VBoxManage setextradata "$1" "VBoxInternal/Devices/piix3ide/0/Config/Port1/SerialNumber" "KLHH54G4324"\t\n')
# logfile.write(
#     'VBoxManage setextradata "$1" "VBoxInternal/Devices/piix3ide/0/Config/Port1/ATAPIVendorId" "Slimtype"\t\n')
# logfile.write(
#     'VBoxManage setextradata "$1" "VBoxInternal/Devices/piix3ide/0/Config/Port1/ATAPIProductId" "DVDRAM GUE2P"\t\n')
# logfile.write('VBoxManage setextradata "$1" "VBoxInternal/Devices/piix3ide/0/Config/Port1/ATAPIRevision" "AS02"\t\n')

logfile.write('else\n')
for k, v in disk_dmi.items():
    if '** No value to retrieve **' in v:
        logfile.write(
            '# VBoxManage setextradata "$1" VBoxInternal/Devices/ahci/0/Config/Port0/' + k + '\t' + v + '\n')
    else:
        logfile.write(
            'VBoxManage setextradata "$1" VBoxInternal/Devices/ahci/0/Config/Port0/' + k + '\t\'' + v + '\'\n')

# CD-Drive

# logfile.write(
#     'VBoxManage setextradata "$1" "VBoxInternal/Devices/ahci/0/Config/Port1/ModelNumber" "HL-DT-ST DVDRAM GUE2P"\t\n')
# logfile.write('VBoxManage setextradata "$1" "VBoxInternal/Devices/ahci/0/Config/Port1/FirmwareRevision" "AS01"\t\n')
# logfile.write('VBoxManage setextradata "$1"
# "VBoxInternal/Devices/ahci/0/Config/Port1/SerialNumber" "KLHH54G4324"\t\n')
# logfile.write('VBoxManage setextradata "$1" "VBoxInternal/Devices/ahci/0/Config/Port1/ATAPIVendorId" "Slimtype"\t\n')
# logfile.write(
#     'VBoxManage setextradata "$1" "VBoxInternal/Devices/ahci/0/Config/Port1/ATAPIProductId" "DVDRAM GUE2P"\t\n')
# logfile.write('VBoxManage setextradata "$1" "VBoxInternal/Devices/ahci/0/Config/Port1/ATAPIRevision" "AS02"\t\n')
logfile.write('fi\n')

# # Get and write DSDT image to file - removed since DSDT file of my device is too big >64kb
# print('[*] Creating a DSDT file...')
# name_of_dsdt = dmi_info['DmiSystemProduct'].replace(' ', '').replace('string:', '')
# if name_of_dsdt:
#     dsdt_name = 'DSDT_' + dmi_info['DmiSystemProduct'].replace(" ", "").replace("/", "_").replace("string:",
#                                                                                                   "") + '.bin'
#     os.system("dd if=/sys/firmware/acpi/tables/DSDT of=" + dsdt_name + " >/dev/null 2>&1")
# else:
#     dsdt_name = 'DSDT_' + dmi_info['DmiChassisType'] + '_' + dmi_info['DmiBoardProduct'].replace("string:",
#                                                                                                  "") + '.bin'
#     os.system("dd if=/sys/firmware/acpi/tables/DSDT of=" + dsdt_name + " >/dev/null 2>&1")
#
try:
    if Path(DSDT_FILE).is_file():
        logfile.write(
            'if [ ! -f "' + DSDT_FILE + '" ]; then echo "[WARNING] Unable to find the DSDT file!"; fi\t\n')
        logfile.write(
            'VBoxManage setextradata "$1" VBoxInternal/Devices/acpi/0/Config/CustomTable ' + DSDT_FILE + '\t\n')
except Exception:
    print('[WARNING] Unable to create the DSDT dump')
    pass

acpi_dsdt = subprocess.getoutput(r'acpidump -s | grep DSDT | grep -o "\(([A-Za-z0-9].*)\)" | tr -d "()"')
acpi_facp = subprocess.getoutput(r'acpidump -s | grep FACP | grep -o "\(([A-Za-z0-9].*)\)" | tr -d "()"')

if "option requires" in acpi_dsdt:
    acpi_error = subprocess.getoutput("lsb_release -r | awk {' print $2 '}")
    print('The version of acpidump included in', acpi_error, 'is not supported')
    exit()
else:
    acpi_list_dsdt = acpi_dsdt.split(' ')
    acpi_list_dsdt = list(filter(None, acpi_list_dsdt))

    acpi_list_facp = acpi_facp.split(' ')
    acpi_list_facp = list(filter(None, acpi_list_facp))

# An attempt to solve some of the issues with the AcpiCreatorRev values, I blame the VBox team ..
if isinstance(acpi_list_dsdt[5], str):
    acpi_list_dsdt[5] = re.sub("[^0-9]", "", acpi_list_dsdt[5])

logfile.write(
    'VBoxManage setextradata "$1" VBoxInternal/Devices/acpi/0/Config/AcpiOemId\t\'' + acpi_list_dsdt[1] + '\'\n')
logfile.write('VBoxManage setextradata "$1" VBoxInternal/Devices/acpi/0/Config/AcpiCreatorId\t\'' + acpi_list_dsdt[
    4] + '\'\n')
logfile.write('VBoxManage setextradata "$1" VBoxInternal/Devices/acpi/0/Config/AcpiCreatorRev\t\'' + acpi_list_dsdt[
    5] + '\'\n')

# Copy and set the CPU brand string
cpu_brand = subprocess.getoutput("cat /proc/cpuinfo | grep -m 1 'model name' | cut -d  ':' -f2 | sed 's/^ *//'")

if len(cpu_brand) < 47:
    cpu_brand = cpu_brand.ljust(47, ' ')

eax_values = ('80000002', '80000003', '80000004')
registers = ('eax', 'ebx', 'ecx', 'edx')

i = 4
while i <= 47:
    for e in eax_values:
        for r in registers:
            k = i - 4  # type: ignore
            if len(cpu_brand[k:i]):  # type: ignore
                rebrand = subprocess.getoutput(
                    "echo -n '" + cpu_brand[k:i] + "' |od -A n -t x4 | sed 's/ //'")  # type: ignore
                logfile.write(
                    'VBoxManage setextradata "$1" '
                    'VBoxInternal/CPUM/HostCPUID/' + e + '/' + r + '  0x' + rebrand + '\t\n')
            i = i + 4

# needs patch of vbox
# logfile.write(f'VBoxManage setextradata "$1" VBoxInternal/Devices/acpi/0/Config/DsdtFilePath {ACPI_DSDT_FILE}\t\n')
# logfile.write(f'VBoxManage setextradata "$1" VBoxInternal/Devices/acpi/0/Config/SsdtFilePath {ACPI_SSDT_FILE}\t\n')
logfile.write(f'VBoxManage setextradata "$1" VBoxInternal/Devices/vga/0/Config/BiosRom {VIDEO_FILE}\t\n')
logfile.write(f'VBoxManage setextradata "$1" VBoxInternal/Devices/pcbios/0/Config/BiosRom {PCBIOS_FILE}\t\n')
logfile.write(f'VBoxManage setextradata "$1" VBoxInternal/Devices/pcbios/0/Config/LanBootRom {PXE_FILE}\t\n')
logfile.write('VBoxManage modifyvm "$1" --chipset ich9\t\n')
logfile.write('VBoxManage modifyvm "$1" --hwvirtex on\t\n')
logfile.write('VBoxManage modifyvm "$1" --vtxvpid on\t\n')
logfile.write('VBoxManage modifyvm "$1" --vtxux on\t\n')
logfile.write('VBoxManage modifyvm "$1" --apic on\t\n')
logfile.write('VBoxManage modifyvm "$1" --pae on\t\n')
logfile.write('VBoxManage modifyvm "$1" --longmode on\t\n')
logfile.write('VBoxManage modifyvm "$1" --hpet on\t\n')
logfile.write('VBoxManage modifyvm "$1" --nestedpaging on\t\n')
logfile.write('VBoxManage modifyvm "$1" --largepages on\t\n')
logfile.write('VBoxManage modifyvm "$1" --graphicscontroller vmsvga\t\n')
logfile.write('VBoxManage modifyvm "$1" --mouse ps2\t\n')
logfile.close()
