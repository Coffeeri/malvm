# malvm

The tool malvm is used to create sanitized virtual environments, such that a
Maleware is not able to determine, if it's in a virtual machine or not.

## Characteristics

malvm uses different characteristics. Each having its own `check` and `fix` method.
All Characteristic definitions are in `src/malvm/characteristics/` defined.
All modules in this package will be dynamically loaded.
Each Module has a class, which inherits from `Characteristic`in 
`src/malvm/characteristics/abstract_characteristic.py`.
Each Characteristic-Module can have multiple Sub-Characteristics.
In the example of `FilesCharacteristic` - each File would be its own
Sub-Characteristic.

## Installation

Clone this repository and install the package.

### Development
```shell
./bootstrap.sh
```

### Normal User
```shell
git clone git@gitlab.com:shk_fkie/analysevm.git

cd analysevm

python setup.py install

```

Now you are able to use the commandline.

## Commandline

### Build VMs
```shell
malvm box build # Select template interactive or as Argument
malvm box run <TEMPLATE> <VM NAME>

# Example:
malvm box build win10_1607_x64_analyst 
malvm box run win10_1607_x64_analyst AnalysisVM01

# (Chained)
malvm box build win10_1607_x64_analyst run win10_1607_x64_analyst AnalysisVM01
```

### Check and Fix VM characteristics

To check and/ or fix given characteristics, run:

```shell
malvm check <None | characteristics>

# check and fix
malvm fix <None | characteristics>

# Example:
malvm fix # Checks and fixes all characteristics
```