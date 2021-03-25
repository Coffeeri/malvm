<div align="center">
<img src="https://gitlab.com/uploads/-/system/project/avatar/18734431/computer.png" align="center" width="150" alt="Project icon">
<h1>malvm</h1>
<h4>Build non detectable Virtual Machines for malware analysis.</h4>
<h4>We currently only support Linux!</h4>

![pipeline](https://gitlab.com/shk_fkie/analysevm/badges/master/pipeline.svg "Pipeline")
</div>


The tool malvm is used to create sanitized virtual environments, such that a
malware is not able to determine, if it's in a virtual environment or not.
Create and integrate your own analysis images:

+ **Build:** OS images with [Packer](https://www.packer.io/) and deploy them with [Vagrant](https://www.vagrantup.com/). All centralized controlled by malvm.
+ **Configure:** Set your settings such as logging and default VM configuration.
  Predefine your environment in *malvm_config.yaml* and build + deploy it with `malvm up`.
+ **Integrate:** Add your own characteristic fixes and let malvm run them inside your VM.
+ **Extendable:** The entire project is build very modular, you can integrate your own hypervisor,
view and (sub-)controller.

## Getting Started
### Table of Content

1. [Prerequisite](#prerequisite)
2. [Installation](#install-malvm)
3. [Quick start: Create your first VM](#first-vm)
4. [Quick start: Check and Fix your VM-Environment](#checks-and-fixes)
5. [Implementation of characteristics](#Characteristics)

### Prerequisite
Please make sure that the following dependencies are installed:

0. Make sure your host runs on a linux os.
1. [Python3](https://www.python.org/downloads/)
2. [git](https://git-scm.com/downloads)
3. [Vagrant](https://www.vagrantup.com/downloads)
4. [Packer](https://learn.hashicorp.com/packer/getting-started/install) (malvm v0.0.1 tested with packer 1.5.6; malvm v0.0.2 tested with packer 1.6.5)
5. [VirtualBox](https://www.virtualbox.org/wiki/Downloads) 

---

### Install malvm

#### with pip

You need to create a [personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).

```shell
pip install --extra-index-url https://__token__:YOUR_ACCESS_TOKEN@gitlab.com/api/v4/projects/18734431/packages/pypi/simple malvm
```

---

#### with git clone and manual Installation

Please make sure that you installed all packages in [Prerequisite](#prerequisite).

##### **1. Clone the Repository and open a shell in the folder.**
```shell
git clone git@gitlab.com:shk_fkie/analysevm.git
```

```shell
cd analysevm
```

##### **2. Install package**

**2.1 Install package (Normal User)**

```shell
python setup.py install
```

**2.1 Install package (Developer)**

```shell
source bootstrap.sh
```

---

### First VM

In the following we are going to create a Windows 10 VM called "malwareVM".
We use two commands chained together.

```shell
malvm box build windows_10
malvm box run malwareVM windows_10
```
First `malware box build windows_10` builds the Windows 10 image for Vagrant.
Next `malvm box run malwareVM windows_10` spins up a Virtual Machine instance of the 
previously created image.

Both commands can be chained into a single command:
```shell
malvm box build windows_10 run malwareVM windows_10
```

---

### Checks and Fixes 

Malvm analyses its environment. It includes 
[Characteristics](https://gitlab.com/shk_fkie/analysevm/-/wikis/2.-Characteristics) 
which reveal the existence of being in a VM-environment.

Those characteristics can be checked with:

```shell
malvm check
```

If those failed ones should be fixed, simply run:

```shell
malvm fix
```

---

## Characteristics

malvm uses different characteristics, each having its own `check` and `fix` method.
All Characteristic definitions are in `src/malvm/characteristics/` defined.
All modules in this package will be dynamically loaded.

Each Module defines a characteristic and consists of a class, which inherits from `Characteristic` class in 
`src/malvm/characteristics/abstract_characteristic.py`.

Each Characteristic-Module can have multiple Sub-Characteristics.
In the example of `FilesCharacteristic` - each File would be its own
Sub-Characteristic.