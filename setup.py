#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Malvm Setup.py configuration."""
import glob
import shutil

import setuptools

from malvm.utils.helper_methods import get_data_dir, get_vm_malvm_egg

DATA_FILES = [str(file.absolute()) for file in get_data_dir().rglob("*")]
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
for file in glob.glob(r"./dist/malvm*.egg"):
    shutil.copy(file, str(get_vm_malvm_egg().absolute()))
