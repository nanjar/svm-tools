#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Update SVM application from github:
# Shakecontroller, smartvending server and smartvending client
#
# hesaputra@2021
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

SHAKECONTROLLER_PATH=/smartvending/controller
SMARTVENDING_SERVER_PATH=/smartvending/server
SMARTVENDING_CLIENT_PATH=/smartvending/client
SMARTVENDING_SVM_TOOLS_PATH=/opt/svm-tools

# Update shakecontroller
if [ -d $SHAKECONTROLLER_PATH ]; then
    echo 'Updating controller...'
    cd $SHAKECONTROLLER_PATH
    git reset --hard HEAD
    git pull --no-edit
fi

# Update smartvending server
if [ -d $SMARTVENDING_SERVER_PATH ]; then
    echo 'Updating smartvending server...'
    cd $SMARTVENDING_SERVER_PATH
    git pull --no-edit
fi

# Update smartvending client
if [ -d $SMARTVENDING_CLIENT_PATH ]; then
    echo 'Updating smartvending client...'
    cd $SMARTVENDING_CLIENT_PATH
    git pull --no-edit
fi

# Update svm-tools
if [ -d $SMARTVENDING_SVM_TOOLS_PATH ]; then
    echo 'Updating svm-tools...'
    cd $SMARTVENDING_SVM_TOOLS_PATH
    sudo unlock-system -p
    git reset --hard HEAD
    git pull --no-edit
    sudo lock-system
fi



