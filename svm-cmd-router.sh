#!/bin/bash

SCRIPT_NAME="svm-cmd-router"

ENV_NAME="asset-$SCRIPT_NAME/env"
CALLER_DIR="$PWD"
PY_BASE_DIR=$(readlink -f $0 | xargs dirname)/py
ENV_DIR="$PY_BASE_DIR/$ENV_NAME"

if [ ! -d "$ENV_DIR" ]; then
  sudo unlock-system
  echo "Creating env only for the first time..."
  python3 -m venv $ENV_DIR
  source $ENV_DIR/bin/activate
  echo "Installing necessary packages..."
  cd $PY_BASE_DIR
  pip3 install -r "asset-$SCRIPT_NAME"/requirements.txt
  deactivate
  sudo lock-system
  cd $CALLER_DIR
  echo "Packages installation is done."
  echo ""
fi

deactivate > /dev/null 2>&1
source $ENV_DIR/bin/activate
python3 "$PY_BASE_DIR/$SCRIPT_NAME.py" "$@"

