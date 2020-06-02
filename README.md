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

```shell
git clone git@gitlab.com:shk_fkie/analysevm.git

cd analysevm

python setup.py install

```

Now you are able to use the commandline.

## Commandline

```shell
Usage: malvm [OPTIONS] COMMAND [ARGS]...

  Base CLI-command for malvm.

Options:
  --help  Show this message and exit.

Commands:
  check  [Optional: code] Checks satisfaction of CHARACTERISTIC.
  fix    [Optional: code] Fixes satisfaction of CHARACTERISTIC.
  show   [Optional: -a --show-all to include sub characteristics] Lists all characteristics.
```