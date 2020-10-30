#!/usr/bin/env bash
pip3 install virtualenv
virtualenv -p python3.8 venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 setup.py install
