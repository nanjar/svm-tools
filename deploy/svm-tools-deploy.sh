#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# svm-tools deploy script
# 
#
# hesaputra@2022
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

sudo unlock-system -p

# Deploy to /usr/bin
sudo ln -sf /opt/svm-tools/svm-update.sh /usr/bin/svm-update
sudo ln -sf /opt/svm-tools/svm-check-services.sh /usr/bin/svm-check-services
sudo ln -sf /opt/svm-tools/svm-cmd-router.sh /usr/bin/svm-cmd-router
sudo ln -sf /opt/svm-tools/svm-tail-log.sh /usr/bin/svm-tail-log
sudo ln -sf /opt/svm-tools/svm-ts-calib.sh /usr/bin/svm-ts-calib
sudo ln -sf /opt/svm-tools/svm-lock-machine.sh /usr/bin/svm-lock-machine
sudo ln -sf /opt/svm-tools/virtual-button/virtual-button.sh /usr/bin/virtual-button
sudo ln -sf /opt/svm-tools/svm-show-maintenance-image.sh /usr/bin/show-maintenance

# Install env variable
sudo ln -s /opt/svm-tools/config/env-variable/svm-env.sh /etc/profile.d/svm-env.sh

# Install services
sudo cp -f /opt/svm-tools/config/systemd/svm-zero-init.service /etc/systemd/system/
sudo systemctl enable svm-zero-init.service

sudo cp -f /opt/svm-tools/config/systemd/svm-preps.service /etc/systemd/system/
sudo systemctl enable svm-preps.service

sudo cp -f /opt/svm-tools/config/systemd/fake-hwclock.service /etc/systemd/system/
sudo systemctl enable fake-hwclock.service

sudo cp -f /opt/svm-tools/config/systemd/svm-scheduled-restart.service /etc/systemd/system/
sudo systemctl enable svm-scheduled-restart.service
sudo systemctl daemon-reload
sudo lock-system





