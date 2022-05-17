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
SMARTVENDING_TEST_SUITE_PATH=/opt/svm-test-suite

# Update shakecontroller
if [ -d $SHAKECONTROLLER_PATH ]; then
    echo 'Updating controller...'
    cd $SHAKECONTROLLER_PATH
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

# Update smartvending test suite
if [ -d $SMARTVENDING_TEST_SUITE_PATH ]; then
    echo 'Updating smartvending test suite...'
    cd $SMARTVENDING_TEST_SUITE_PATH
    sudo unlock-system -p
    git pull --no-edit
    sudo lock-system
fi

