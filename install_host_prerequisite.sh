#!/usr/bin/env bash

#INSTALL_PATH="/usr/bin/"
INSTALL_PATH="$HOME/.local/bin/"
VAGRANT_VERSION="2.2.14"
PACKER_VERSION="1.6.5"

VAGRANT_DOWNLOAD_URL_LINUX="https://releases.hashicorp.com/vagrant/${VAGRANT_VERSION}/vagrant_${VAGRANT_VERSION}_linux_amd64.zip"
# VAGRANT_DOWNLOAD_URL_DEBIAN="https://releases.hashicorp.com/vagrant/${VAGRANT_VERSION}/vagrant_${VAGRANT_VERSION}_x86_64.deb"

PACKER_DOWNLOAD_URL_LINUX="https://releases.hashicorp.com/packer/${PACKER_VERSION}/packer_${PACKER_VERSION}_linux_amd64.zip"

IS_DEBIAN=false
EXIT_CODE=0



check_vagrant_installed()
{
  if command -v vagrant &> /dev/null
  then
    return 0
  else
    return 1
  fi
}
install_vagrant()
{
  curl -o /tmp/vagrant.zip ${VAGRANT_DOWNLOAD_URL_LINUX}
  unzip /tmp/vagrant.zip -d ${INSTALL_PATH}
  check_vagrant_installed
  if [ $? -eq "0" ]
  then
      VAGRANT_VERSION_INSTALLED=`vagrant --version | tr -d "Vagrant "`
      if [ "${VAGRANT_VERSION_INSTALLED}" = "${VAGRANT_VERSION}" ]
      then
        echo "Vagrant ${VAGRANT_VERSION} was successfully installed."
        echo "Repairing Vagrant, this is neccessary.."
        vagrant plugin expunge --reinstall -f
      else
        echo "ERROR: Vagrant ${VAGRANT_VERSION} was NOT successfully installed!"
        EXIT_CODE=1
      fi
  else
      echo "ERROR: Vagrant ${VAGRANT_VERSION} was NOT successfully installed!"
      EXIT_CODE=1
  fi
}

check_packer_installed()
{
  if command -v packer &> /dev/null
  then
    return 0
  else
    return 1
  fi
}

install_packer()
{
  curl -o /tmp/packer.zip ${PACKER_DOWNLOAD_URL_LINUX}
  unzip /tmp/packer.zip -d ${INSTALL_PATH}
  check_packer_installed
  if [ $? -eq "0" ]
  then
      PACKER_VERSION_INSTALLED=`packer --version`
      if [ "${PACKER_VERSION_INSTALLED}" = "${PACKER_VERSION}" ]
      then
          echo "Packer ${PACKER_VERSION} was successfully installed."
      else
          echo "ERROR: Packer ${PACKER_VERSION} was NOT successfully installed!"
          EXIT_CODE=1
      fi
  else
      echo "ERROR: Packer ${PACKER_VERSION} was NOT successfully installed!"
      EXIT_CODE=1
  fi
}


# Check OS
if [ -d "/etc/debian_version" ]
then
    echo "Found: Debian based OS."
    # Debian/ Ubuntu distro
    IS_DEBIAN=true
    apt update && apt install -y curl unzip

else
    echo "Found: No Debian based OS, fallback to other Linux OS."
    # Other Linux
    IS_DEBIAN=false

fi

################## Start of script ##################
# Check current vagrant version
check_vagrant_installed
if [ $? -eq "0" ]
then
    VAGRANT_VERSION_INSTALLED=`vagrant --version | tr -d "Vagrant "`
    echo "Found: Vagrant with version ${VAGRANT_VERSION_INSTALLED}"

    if [ ! "${VAGRANT_VERSION_INSTALLED}" = "${VAGRANT_VERSION}" ]
    then
        echo "Vagrant version ${VAGRANT_VERSION} was expected."
        read -p "Should expected Vagrant ${VAGRANT_VERSION} be installed (y/n)?" choice
        case "$choice" in
          y|Y ) install_vagrant;;
          n|N ) echo "Ok, skipped.";;
          * ) echo "invalid answer.";;
        esac
    fi
else
    echo "Vagrant not found. Attempting install.."
    install_vagrant
fi


# Check current packer version
check_packer_installed
if [ $? -eq "0" ]
then
    PACKER_VERSION_INSTALLED=`packer --version`
    echo "Found: Packer with version ${PACKER_VERSION_INSTALLED}"

    if [ ! "${PACKER_VERSION_INSTALLED}" = "${PACKER_VERSION}" ]
    then
        echo "Packer version ${PACKER_VERSION} was expected."
        read -p "Should expected Packer ${PACKER_VERSION} be installed (y/n)?" choice
        case "$choice" in
          y|Y ) install_packer;;
          n|N ) echo "Ok, skipped.";;
          * ) echo "invalid answer.";;
        esac
    fi
else
    echo "Packer not found. Attempting install.."
    install_packer
fi


exit $EXIT_CODE