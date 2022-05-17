#!/bin/bash

ENV_NAME="asset-virtual-button/env"
CALLER_DIR="$PWD"
PY_BASE_DIR=$(readlink -f $0 | xargs dirname)/py
ENV_DIR="$PY_BASE_DIR/$ENV_NAME"

if [ ! -d "$ENV_DIR" ]; then
  sudo unlock-system
  echo "Creating env only for the first time..."
  sudo python3 -m venv $ENV_DIR
  sudo chown pi.pi -R $ENV_DIR
  source $ENV_DIR/bin/activate
  echo "Installing necessary packages..."
  cd $PY_BASE_DIR
  pip3 install -r requirements.txt
  deactivate
  sudo lock-system
  cd $CALLER_DIR
  echo "Packages installation is done."
  echo ""
fi

source $ENV_DIR/bin/activate
python3 $PY_BASE_DIR/virtual-button.py


