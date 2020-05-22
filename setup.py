"""This file contains package details."""
import setuptools

setuptools.setup(
    name="malvm",
    version="0.0.1",
    install_requires=["click"],
    author="Leander Kohler",
    author_email="leander.kohler@uni-bonn.de",
    description="Creates non detectable VMs to analyze Malware.",
    url="https://gitlab.com/shk_fkie/analysevm/",
    packages=setuptools.find_packages(),
    classifiers=["Programming Language :: Python :: 3",],
    python_requires=">=3.6",
)
