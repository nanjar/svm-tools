import subprocess
import threading
import datetime
import pathlib
import time
import os

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
IS_LOG_ENABLE = False
LOG_PATH = '/var/log/smartvending/system/svm-scheduled-restart.log'

__lock_log = threading.Lock()


def write_log(message: str):
    global LOG_PATH
    global IS_LOG_ENABLE
    global __lock_log

    __lock_log.acquire()
    if IS_LOG_ENABLE:
        if time.daylight:
            system_tz = datetime.timezone(datetime.timedelta(seconds=-time.altzone), time.tzname[1])
        else:
            system_tz = datetime.timezone(datetime.timedelta(seconds=-time.timezone), time.tzname[0])

        with open(LOG_PATH, "a") as fd:
            fd.write(str(datetime.datetime.now(system_tz).isoformat(sep=' ', timespec='milliseconds')) + ' [DEBUG]: [SvmScheduledRestart] ' + str(message) + '\r\n')
    __lock_log.release()


def get_fake_hwclock_datafile() -> str:
    fake_hwclock_cmd = 'fake-hwclock'
    fake_hwclock_dataenv = 'FILE'
    fake_hwclock_default_datafile = '/etc/fake-hwclock.data'

    # Check if fake-hwclock is available
    output = subprocess.run(['command', '-v', fake_hwclock_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if output is not None and len(output.stdout) > 0:
        datafile = os.environ.get(fake_hwclock_dataenv)
        if datafile is not None:
            return datafile
        else:
            # Return default path
            if os.path.exists(fake_hwclock_default_datafile):
                return fake_hwclock_default_datafile
            else:
                return ''
    else:
        return ''


def get_system_time_utc() -> datetime:
    return datetime.datetime.utcnow()


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
        write_log("Current system time: " + str(get_system_time_utc))
        time.sleep(1)

    # while True:
    #     ui_state = is_ui_idle()
    #     if ui_state is not None:
    #         if ui_state:
    #             # Show scheduled restart image
    #             subprocess.Popen(['python3', '/opt/svm-tools/py/svm-show-image.py', '--file', SCHEDULED_MAINTENANCE_IMG_FILE, '--display', ':0.0'])
    #
    #             # Stop ui
    #             subprocess.call(['pm2', 'stop', 'all'])
    #
    #             # Restart router
    #             subprocess.call(['/opt/svm-tools/svm-cmd-router.sh', '--reboot'])
    #
    #             # Save current time to fake-hwclock data
    #             subprocess.call(['/usr/sbin/fake-hwclock', 'save', 'force'])
    #             time.sleep(5)
    #
    #             # Restart raspi
    #             subprocess.call(['sudo', '/usr/sbin/reboot', 'now'])
    #
    #             break
    #         else:
    #             time.sleep(DELAY_IF_BUSY_SECOND)
    #     else:
    #         print("Error: Unable to find", UI_STATE_FILE, ". Please update shakecontroller.")
    #         break






# import pathlib
# import time
# import subprocess
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# #  svm-scheduled-restart
# #
# #  Schedule restart router and raspberry pi system
# #
# #
# #  HS@2022
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
# UI_STATE_FILE = '/var/run/smartvending/ui.state'
# SCHEDULED_MAINTENANCE_IMG_FILE = '/opt/svm-tools/img/svm-img-scheduled-maintenance.png'
#
# DELAY_IF_BUSY_SECOND = 300
#
#
# def is_ui_idle() -> bool:
#     try:
#         if pathlib.Path(UI_STATE_FILE).read_text().strip() == 'idle':
#             return True
#         else:
#             return False
#     except:
#         return None
#
#
# if __name__ == '__main__':
#     while True:
#         ui_state = is_ui_idle()
#         if ui_state is not None:
#             if ui_state:
#                 # Show scheduled restart image
#                 subprocess.Popen(['python3', '/opt/svm-tools/py/svm-show-image.py', '--file', SCHEDULED_MAINTENANCE_IMG_FILE, '--display', ':0.0'])
#
#                 # Stop ui
#                 subprocess.call(['pm2', 'stop', 'all'])
#
#                 # Restart router
#                 subprocess.call(['/opt/svm-tools/svm-cmd-router.sh', '--reboot'])
#
#                 # Save current time to fake-hwclock data
#                 subprocess.call(['/usr/sbin/fake-hwclock', 'save', 'force'])
#                 time.sleep(5)
#
#                 # Restart raspi
#                 subprocess.call(['sudo', '/usr/sbin/reboot', 'now'])
#
#                 break
#             else:
#                 time.sleep(DELAY_IF_BUSY_SECOND)
#         else:
#             print("Error: Unable to find", UI_STATE_FILE, ". Please update shakecontroller.")
#             break
