# Detection of Virtual Machines (VMs)

The following concepts are restricted to **Windows 7/ 10**.

---

## **Registry Check**

Some registry entries set by hypervisor.

### **VMware**

- HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\0000\DriverDesc
    - VMware SCSI Controller
- HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\0000\ProviderName
    - VMware, Inc.

### **VirtualBox**

Coming soon.

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

Maleware can test IN instruction, which is privileged (Ring 0).
If it is executed in Ring 3, it will throw usually an exception.
However no exception will be thrown within a VM, instead will e connection be raised with the host and Magic Number "*VMxh*" is returned into *EBX* register.

---

## **Processes and Files Check**

Some helper programs reveal the existence of the hypervisor such as *VMwareService.exe*.

---

## **MAC check**

Devices such as Network, CD-Roms etc have **MAC addresses** which can be reduced to VMware/ VirtualBox.

- VMWare 00-05-69, 00-0c-29, 00-1c-14 or 00-50-56
- VirtualBox 08-00-27

The **BIOS serial number** does also reveal the existence of the hypervisor.

---

## **Other Hardware Check**

Malware queries various attributes like SerialNo, SocketDesignation..

---

## Reference

- https://resources.infosecinstitute.com/how-malware-detects-virtualized-environment-and-its-countermeasures-an-overview/
https://www.cyberbit.com/blog/endpoint-security/anti-vm-and-anti-sandbox-explained/