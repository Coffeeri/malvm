"""This file contains package details."""
import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="malvm", # Replace with your own username
    version="0.0.1",
    install_requires=requirements,
    author="Leander Kohler",
    author_email="leander.kohler@uni-bonn.de",
    description="Creates non detectable VMs to analyze Malware.",
    url="https://gitlab.com/shk_fkie/analysevm/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
