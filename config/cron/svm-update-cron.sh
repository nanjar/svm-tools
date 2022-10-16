#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Update cron job from cron_task to system
#
# hesaputra@2022
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

sudo unlock-system
crontab -u pi /opt/svm-tools/config/cron/cron_task
sudo lock-system
sudo systemctl restart cron.service
