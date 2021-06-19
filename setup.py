#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Malvm Setup.py configuration."""
import glob
import shutil
import sys
from pathlib import Path
import codecs
import os.path
import setuptools


def get_config_root() -> Path:
    """Returns path for config and temp files."""
    platform = sys.platform.lower()
    if platform in ["linux", "linux2", "darwin"]:
        config_path = Path.home() / ".local/share/malvm"
    elif platform in ["windows", "win32"]:
        config_path = Path.home().absolute() / "/AppData/Local/malvm"
    else:
        raise OSError(f"Your platform <{platform}> is not supported by malvm.")

    if not config_path.exists():
        config_path.mkdir(parents=True)
    return config_path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


DATA_FILES = [
    str(file.absolute())
    for file in (Path(__file__).parent / "src/malvm/data").rglob("*")
]

setuptools.setup(
    name="malvm",
    version=get_version("src/malvm/__init__.py"),
    author="Leander Kohler",
    author_email="leander.kohler@uni-bonn.de",
    description="Creates non detectable VMs to analyze Malware.",
    classifiers=["Programming Language :: Python :: 3"],
    url="https://gitlab.com/shk_fkie/analysevm/",
    project_urls={"GitLab.com Source": "https://gitlab.com/shk_fkie/analysevm/"},
    python_requires=">=3.6",
    packages=setuptools.find_packages(where="src"),
    package_dir={"malvm": "src/malvm"},
    install_requires=["click", "inquirer", "pyyaml",
                      'wmi; platform_system=="Windows"'],
    package_data={"malvm": DATA_FILES},
    entry_points={"console_scripts": ["malvm = malvm.__main__:main"]},
)
# Add malvm installation file to config folder
# Needed for installing malvm on each Virtual Machine
for file in glob.glob(r"dist/malvm*.tar.gz"):
    shutil.copy(file, str((get_config_root() / "malvm.tar.gz").absolute()))
