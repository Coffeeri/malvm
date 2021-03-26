# Detection of Virtual Machines (VMs)

The following concepts are restricted to **Windows 7/ 10**.

---

## **Registry Check**

Some registry entries set by hypervisor.

### **Generic**

- \HKEY_LOCAL_MACHINE\HARDWARE\DEVICEMAP\Scsi\Scsi Port 0\Scsi Bus 0\Target Id 0\Logical Unit Id 0\”Identifier”; ”<value>”
- \HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\SystemBiosVersion\ SystemBiosVersion”;”<value>”

### **VMware**

- HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\0000\DriverDesc
    - VMware SCSI Controller
- HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\0000\ProviderName
    - VMware, Inc.
- HKLM\SOFTWARE\Vmware Inc.\\\Vmware Tools
- HKEY_LOCAL_MACHINE\HARDWARE\DEVICEMAP\Scsi\Scsi Port 2\Scsi Bus 0\Target Id 0\Logical Unit Id 0\Identifier
- SYSTEM\CurrentControlSet\Enum\SCSI\Disk&Ven_VMware_&Prod_VMware_Virtual_S
- SYSTEM\CurrentControlSet\Control\CriticalDeviceDatabase\root#vmwvmcihostdev
- SYSTEM\CurrentControlSet\Control\VirtualDeviceDrivers


    

### **VirtualBox**
- \HKEY_LOCAL_MACHINE\HARDWARE\ACPI\DSDT\VBOX__
- \HKEY_LOCAL_MACHINE\HARDWARE\ACPI\FADT\VBOX__
- \HKEY_LOCAL_MACHINE\HARDWARE\ACPI\RSDT\VBOX__
- \HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\VBox*
- \HKEY_LOCAL_MACHINE\SOFTWARE\Oracle\VirtualBox Guest Additions\*

---

## **Memory Check**

Checks memory structure, especially the *Interrupt Descriptor Table* (IDT) varies in VMs compared to physical machines.
Other points of interests are the following structures:
- Store Local Descriptor Table (SLDT)
- Store Global Descriptor Table (SGDT)
- Store Task Register (STR)


### Example (S)IDT

*Store Interrupt Descriptor Table* (SIDT): In a VM this is typically located at 0xffXXXXXX whereas, in a physical machine, this is located somewhat lower than that typically around 0x80ffffff.

---

## **Communication Channel Check**

Malware can test IN instruction, which is privileged (Ring 0).
If it is executed in Ring 3, it will throw usually an exception.
However no exception will be thrown within a VM, instead will e connection be raised with the host and Magic Number "*VMxh*" is returned into *EBX* register.

There is also the ***CPUID*** instruction.
> https://rayanfam.com/topics/defeating-malware-anti-vm-techniques-cpuid-based-instructions/

Intel & AMD have reserved cpuid levels ***0x40000000 - 0x400000FF*** for
software use. - Ref: Line 89 Commit 8c0b77d https://github.com/fffaraz/Etcetera/blob/master/cpp/cpuid.h or https://kb.vmware.com/s/article/1009458
1
---

## **Processes and Files Check**

Some helper programs reveal the existence of the hypervisor such as *VMwareService.exe*.

### Processes Indicating a VM

via WMIC, Win API and CMD. WMIC (wmic -> process list), Win API (Process32First, Process32Next), and Tasklist.exe.

- Vmware
  - Vmtoolsd.exe
  - Vmwaretrat.exe
  - Vmwareuser.exe
  - Vmacthlp.exe
  - VGAuthService.exe

- VirtualBox
  - vboxservice.exe
  - vboxtray.exe

### Running services

These can also be retrieved in multiple ways WMIC, Win API and CMD
(wmic -> Service list, sc.exe /query) 

- VMTools
- Vmhgfs
- VMMEMCTL
- Vmmouse
- Vmrawdsk
- Vmusbmouse
- Vmvss
- Vmscsi
- Vmxnet
- vmx_svga

- **VMWare**
  - MTools
  - vmvss
  - VGAuthService
  - VMware Physical Disk Helper Service
  - Vmware Tools

- **VirtualBox**
  - VBoxService


### Files

- VMware
  - C:\windows\System32\Drivers\Vmmouse.sys
  - C:\windows\System32\Drivers\vm3dgl.dll
  - C:\windows\System32\Drivers\vmdum.dll
  - C:\windows\System32\Drivers\vm3dver.dll
  - C:\windows\System32\Drivers\vmtray.dll
  - C:\windows\System32\Drivers\VMToolsHook.dll
  - C:\windows\System32\Drivers\vmmousever.dll
  - C:\windows\System32\Drivers\vmhgfs.dll
  - C:\windows\System32\Drivers\vmGuestLib.dll
  - C:\windows\System32\Drivers\VmGuestLibJava.dll
  - C:\windows\System32\Driversvmhgfs.dll
  - C:\Windows\System32\drivers\vmmemctl.sys
  - C:\Windows\System32\drivers\vmrawdsk.sys

- VirtualBox
  - C:\windows\System32\Drivers\VBoxMouse.sys
  - C:\windows\System32\Drivers\VBoxGuest.sys
  - C:\windows\System32\Drivers\VBoxSF.sys
  - C:\windows\System32\Drivers\VBoxVideo.sys
  - C:\windows\System32\vboxdisp.dll
  - C:\windows\System32\vboxhook.dll
  - C:\windows\System32\vboxmrxnp.dll
  - C:\windows\System32\vboxogl.dll
  - C:\windows\System32\vboxoglarrayspu.dll
  - C:\windows\System32\vboxoglcrutil.dll
  - C:\windows\System32\vboxoglerrorspu.dll
  - C:\windows\System32\vboxoglfeedbackspu.dll
  - C:\windows\System32\vboxoglpackspu.dll
  - C:\windows\System32\vboxoglpassthroughspu.dll
  - C:\windows\System32\vboxservice.exe
  - C:\windows\System32\vboxtray.exe
  - C:\windows\System32\VBoxControl.exe

---

## **MAC check**

Devices such as Network, CD-Roms etc have **MAC addresses** which can be reduced to VMware/ VirtualBox.

- VMWare 00-05-69, 00-0c-29, 00-1c-14 or 00-50-56
- VirtualBox 08-00-27, Hyper-V with 00:03:FF

The **BIOS serial number** does also reveal the existence of the hypervisor.

---

## **Other Hardware Check**

Malware queries various attributes like SerialNo, SocketDesignation..

---

## Reference

- https://resources.infosecinstitute.com/how-malware-detects-virtualized-environment-and-its-countermeasures-an-overview/
- https://www.cyberbit.com/blog/endpoint-security/anti-vm-and-anti-sandbox-explained/
- https://www.deepinstinct.com/2019/10/29/malware-evasion-techniques-part-2-anti-vm-blog/
- https://handlers.sans.org/tliston/ThwartingVMDetection_Liston_Skoudis.pdf
- http://unprotect.tdgt.org/images/2/23/Sandbox-Cheatsheet-1.1.pdf
