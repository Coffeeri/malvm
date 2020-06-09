#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Malvm Setup.py configuration."""
import setuptools

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
    install_requires=["click"],
    package_data={"malvm": ["data/*.json"]},
    entry_points={"console_scripts": ["malvm = malvm.__main__:main"]},
)
