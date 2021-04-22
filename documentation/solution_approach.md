# Solution approach

We want to solve the problem of the hypervisor being detected inside a Virtual Machine (VM).
A couple detection methods used by Malware can be fined in ***detection_methods.md***.

However in the following, we will be iterating over some existing approaches, to finally conclude and build our own anti-malware-vm-detection program, which sanitizes a Windows 7/ 10 VM.
This program will by limited to VirtualBox for the beginning.

---

## 1 antivmdetection

> Github https://github.com/nsmfoo/antivmdetection

Tool for VirtualBox, pretty old (2012) - still somewhat active.1

[Features:](https://pentestit.com/antivmdetection-thwart-vm-detection/)

- Randomize BIOS serial.
- Set custom values for SystemBiosVersion, VideoBiosVersion and- SystemBiosDate.
- Enable RAID support.
- Create a new chassis serial number.
- Change firmware revision number.
- Change disk model number.
- Change CD-ROM firmware number.
- Change CD-ROM model number.
- Change CD-ROM vendor name.
- Randomize VM MAC address, based on the host interface MAC.
- Set the numbers of CPUs to be used.
- Set the Virtual Machine memory size.
- Check if hostonlyifs (host-only network interfaces) IP address is- default.
- Check paravirtualization interface.
- Check if audio support is enabled.
- Set custom Differentiated System Description Table (DSDT) information.
- Set custom Fixed ACPI Description Table (FADT) values.
- Set custom Root System Description Table (RSDT) data.
- Set custom Supplemental Descriptive Data Table (SDDT) information.
- Set operating system InstallDate and MachineGuid.
- Depending on the operating system, set DACType and video card type.
- Set the Microsoft Product ID (ProductId) and desktop background.
- Generate random files with the following extensions: .txt, .pdf, .txt, - docx, .doc, .xls, .xlsx, .zip, .png, .jpg, .jpeg, .gif, .bmp, .html, - htm, .ppt, .pptx.
- Associate file extensions.

### **Fulfilled Requirements**

- [ ] Registry Check
- [x] Memory Check - *some*
- [ ] Communication Channel Check
- [ ] Processes and Files Check
- [x] MAC check
- [ ] Other Hardware Check
- [x] Extra - *adds random bloat/ fake files*