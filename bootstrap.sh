#!/usr/bin/env bash
textBold=$(tput bold)
fgYellow=$(tput setaf 3)
fgWhite=$(tput setaf 7)
textReset=$(tput sgr0)
echo "${fgYellow}"
if [ ! -d "venv" ]; then
    echo "${textBold}Setting up environment..${fgWhite}"
    pip3 install virtualenv
    virtualenv -p python3.8 venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    python3 setup.py sdist
    python3 setup.py install
else
    echo "${textBold}Environment already exists."
    echo "Activate environment.."

fi
echo "${fgYellow}"
. ./venv/bin/activate
echo "${textBold}Have fun, bye."
echo "${textReset}"
