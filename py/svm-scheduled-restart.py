import subprocess
import threading
import datetime
import shutil
import dateutil.tz
# from dateutil import tz
# import dateutil
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


SYSTEM_REBOOT_SCHEDULED_LOCAL_TIME = '02:10:00'
WAIT_IF_UI_BUSY_SECOND = 300
IS_LOG_ENABLE = True
LOG_PATH = '/var/log/smartvending/system/svm-scheduled-restart.log'

LOOP_DELAY_SECOND = 5
UI_STATE_FILE = '/var/run/smartvending/ui.state'
SCHEDULED_MAINTENANCE_IMG_FILE = '/opt/svm-tools/img/svm-img-scheduled-maintenance.png'

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
            print(str(datetime.datetime.now(system_tz).isoformat(sep=' ', timespec='milliseconds')) + ' [DEBUG]: [SvmScheduledRestart] ' + str(message))
            fd.write(str(datetime.datetime.now(system_tz).isoformat(sep=' ', timespec='milliseconds')) + ' [DEBUG]: [SvmScheduledRestart] ' + str(message) + '\r\n')
    __lock_log.release()


def get_system_time_utc() -> datetime:
    return datetime.datetime.now(dateutil.tz.tzutc())


def get_system_time_local() -> datetime:
    return get_system_time_utc().astimezone(dateutil.tz.tzlocal())


def is_system_time_ready() -> bool:
    if os.popen('timedatectl status | grep "System clock synchronized"').read().strip() == "System clock synchronized: yes":
        return True
    else:
        return False


def is_ui_idle() -> bool:
    try:
        if pathlib.Path(UI_STATE_FILE).read_text().strip() == 'idle':
            return True
        else:
            return False
    except:
        return None


def exec_system_reboot():
    # Show scheduled restart image
    subprocess.Popen(['python3', '/opt/svm-tools/py/svm-show-image.py', '--file', SCHEDULED_MAINTENANCE_IMG_FILE, '--display', ':0.0'])

    # Stop ui
    subprocess.call(['pm2', 'stop', 'all'])

    # Restart router
    subprocess.call(['/opt/svm-tools/svm-cmd-router.sh', '--reboot'])
    time.sleep(5)

    # Restart raspi
    subprocess.call(['sudo', '/usr/sbin/reboot', 'now'])


def is_next_day(__prev_date_local: datetime) -> bool:
    if (get_system_time_local().date() - __prev_date_local.date()).days > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    # write_log("Starting svm-scheduled-restart...")
    while not is_system_time_ready():
        # write_log("Waiting system time be ready...")
        time.sleep(LOOP_DELAY_SECOND)

    prev_datetime_local = get_system_time_local()
    tmp_dt = datetime.datetime.strptime(SYSTEM_REBOOT_SCHEDULED_LOCAL_TIME, '%H:%M:%S')
    reboot_scheduled_datetime_local = get_system_time_local().replace(hour=tmp_dt.hour, minute=tmp_dt.minute, second=tmp_dt.second)
    write_log("Auto reboot is scheduled at " + reboot_scheduled_datetime_local.strftime("%H:%M:%S"))

    while True:
        system_local_time = get_system_time_local()
        max_elapsed_local_time = system_local_time + datetime.timedelta(seconds=10)

        if is_next_day(prev_datetime_local):
            reboot_scheduled_datetime_local += datetime.timedelta(days=1)
            prev_datetime_local = get_system_time_local()
            # write_log("reboot_scheduled_datetime_local is updated")

        # write_log("Loop...")
        # write_log("system_local_time: " + str(system_local_time))
        # write_log("max_elapsed_local_time: " + str(max_elapsed_local_time))
        # write_log("reboot_scheduled_datetime_local: " + str(reboot_scheduled_datetime_local))
        # write_log("prev_datetime_local: " + str(prev_datetime_local))

        # if reboot_scheduled_datetime_local < system_local_time < max_elapsed_local_time:
        if system_local_time < reboot_scheduled_datetime_local < max_elapsed_local_time:
            write_log("Rebooting system...")
            exec_system_reboot()
            time.sleep(20)

        # write_log("Current time: " + str(get_system_time_local()))
        time.sleep(LOOP_DELAY_SECOND)

