#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Malvm Setup.py configuration."""
import glob
import shutil
import sys
from pathlib import Path

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


DATA_FILES = [
    str(file.absolute())
    for file in (Path(__file__).parent / "src/malvm/data").rglob("*")
]

setuptools.setup(
    name="malvm",
    version="0.0.1",
    author="Leander Kohler",
    author_email="leander.kohler@uni-bonn.de",
    description="Creates non detectable VMs to analyze Malware.",
    classifiers=["Programming Language :: Python :: 3"],
    url="https://gitlab.com/shk_fkie/analysevm/",
    project_urls={"GitLab.com Source": "https://gitlab.com/shk_fkie/analysevm/"},
    python_requires=">=3.6",
    packages=setuptools.find_packages(where="src"),
    package_dir={"malvm": "src/malvm"},
    install_requires=["click", "inquirer"],
    package_data={"malvm": DATA_FILES},
    entry_points={"console_scripts": ["malvm = malvm.__main__:main"]},
)
# Add malvm installation file to config folder
# Needed for installing malvm on each virtual machine
for file in glob.glob(r"dist/malvm*.egg"):
    shutil.copy(file, str((get_config_root() / "malvm.egg").absolute()))
