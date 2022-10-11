#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Update cron job from cron_task to system
#
# hesaputra@2021
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

crontab -u pi /opt/svm-tools/cron/cron_task
sudo systemctl restart cron.service
