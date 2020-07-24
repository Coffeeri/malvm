# malvm

The tool malvm is used to create sanitized virtual environments, such that a
Maleware is not able to determine, if it's in a virtual machine or not.

VMs are build and installed with the [malboxes](https://github.com/GoSecure/malboxes) 
gqtool.

## Characteristics

malvm uses different characteristics. Each having its own `check` and `fix` method.
All Characteristic definitions are in `src/malvm/characteristics/` defined.
All modules in this package will be dynamically loaded.
Each Module has a class, which inherits from `Characteristic`in 
`src/malvm/characteristics/abstract_characteristic.py`.
Each Characteristic-Module can have multiple Sub-Characteristics.
In the example of `FilesCharacteristic` - each File would be its own
Sub-Characteristic.

## Getting Started
### Table of Content

1. [Prerequisite](#prerequisite)
2. [Installation](#install-malvm)
3. [Quick start: Create your first VM](#first-vm)
4. [Quick start: Check and Fix your VM-Environment](#checks-and-fixes)

### Prerequisite
Please make sure that the following dependencies are installed:

1. [Python3](https://www.python.org/downloads/)
2. [git](https://git-scm.com/downloads)
3. [Vagrant](https://www.vagrantup.com/downloads)
4. [Packer](https://learn.hashicorp.com/packer/getting-started/install) (<1.6.0 like version 1.5.6)
5. [VirtualBox](https://www.virtualbox.org/wiki/Downloads) 

### Install malvm

#### **1. Clone the Repository and open a shell in the folder.**
```shell
▶ git clone git@gitlab.com:shk_fkie/analysevm.git
```

```shell
▶ cd analysevm
```

#### **2. Install package**

**2.1 Install package (Normal User)**

```shell
▶ python setup.py install
```

**2.1 Install package (Developer)**

```shell
▶ ./bootstrap.sh
```

### First VM

In the following we are going to create a Windows 10 VM called "malewareVM".
We use two commands chained together.

```shell
▶ maleware box build windows_10
▶ maleware box run windows_10 malewareVM
```
First `maleware box build windows_10` builds the Windows 10 image for Vagrant.
Next `maleware box run windows_10 malewareVM` spins up a VirtualMachine instance of the previously created image.

Both commands can be chained into a single command:
```shell
▶ malvm box build windows_10 run windows_10 malewareVM
```

### Checks and Fixes 

Malvm analyses its environment. It includes [Characteristics](https://gitlab.com/shk_fkie/analysevm/-/wikis/2.-Characteristics) which reveal the existence of being in a VM-environment.

Those characteristics can be checked with:

```shell
▶ malvm check
```

If those failed ones should be fixed, simply run:

```shell
▶ malvm fix
```