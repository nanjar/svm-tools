import pathlib
import time
import subprocess

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  svm-scheduled-restart
#
#  Schedule restart router and raspberry pi system
#
#
#  HS@2022
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


UI_STATE_FILE = '/var/run/smartvending/ui.state'
SCHEDULED_MAINTENANCE_IMG_FILE = '/opt/svm-tools/img/svm-img-scheduled-maintenance.png'

DELAY_IF_BUSY_SECOND = 300


def is_ui_idle() -> bool:
    try:
        if pathlib.Path(UI_STATE_FILE).read_text().strip() == 'idle':
            return True
        else:
            return False
    except:
        return None


if __name__ == '__main__':
    while True:
        ui_state = is_ui_idle()
        if ui_state is not None:
            if ui_state:
                # Show scheduled restart image
                subprocess.Popen(['python3', '/opt/svm-tools/py/svm-show-image.py', '--file', SCHEDULED_MAINTENANCE_IMG_FILE, '--display', ':0.0'])

                # Stop ui
                subprocess.call(['pm2', 'stop', 'all'])
                
                # Restart router
                subprocess.call(['/opt/svm-tools/svm-cmd-router.sh', '--reboot'])
                time.sleep(5)
                
                # Restart raspi
                subprocess.call(['sudo', 'bash', '-c', 'reboot', 'now'])

                break
            else:
                time.sleep(DELAY_IF_BUSY_SECOND)
        else:
            print("Error: Unable to find", UI_STATE_FILE, ". Please update shakecontroller.")
            break
