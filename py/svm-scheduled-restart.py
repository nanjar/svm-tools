import subprocess
import threading
import datetime

import dateutil.tz
# from dateutil import tz
import dateutil
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


SYSTEM_REBOOT_LOCAL_TIME_H_M_S = '15:50:00'
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


def get_system_time_local() -> datetime:
    return get_system_time_utc().replace(tzinfo=dateutil.tz.tzlocal())


def is_system_time_ready() -> bool:
    fake_hwclock_datafile = get_fake_hwclock_datafile()
    if len(fake_hwclock_datafile) > 0:
        # fake_hwclock data is stored in UTC format, data e.g: 2022-10-15 04:30:35
        with open(fake_hwclock_datafile, 'r') as fd:
            # output = fd.read().strip()
            fake_hwclock_datetime = datetime.datetime.strptime(fd.read().strip() + '+0', '%Y-%m-%d %H:%M:S%z')
            write_log("fake_hwclock_datetime: " + str(fake_hwclock_datetime))
        if get_system_time_utc() > fake_hwclock_datetime:
            return True
        else:
            return False
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

    # Save current time to fake-hwclock data
    subprocess.call(['/usr/sbin/fake-hwclock', 'save', 'force'])
    time.sleep(5)

    # Restart raspi
    subprocess.call(['sudo', '/usr/sbin/reboot', 'now'])


def is_next_day(__prev_date_local: datetime) -> bool:
    if get_system_time_local().date() - __prev_date_local().date() > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    write_log("Starting svm-scheduled-restart...")
    while not is_system_time_ready():
        write_log("Waiting system time be ready...")
        time.sleep(LOOP_DELAY_SECOND)

    prev_datetime_local = get_system_time_local()
    tmp_dt = datetime.datetime.strptime(SYSTEM_REBOOT_LOCAL_TIME_H_M_S, '%H:%M:%S')
    reboot_scheduled_datetime_local = get_system_time_local().replace(hour=tmp_dt.hour, minute=tmp_dt.minute, second=tmp_dt.second)

    while True:
        system_local_time = get_system_time_local()
        max_elapsed_local_time = system_local_time + datetime.timedelta(seconds=10)

        write_log("Loop...")
        write_log("system_local_time: " + str(system_local_time))
        write_log("max_elapsed_local_time: " + str(max_elapsed_local_time))

        if reboot_scheduled_datetime_local < system_local_time < max_elapsed_local_time:
            # exec_system_reboot()
            write_log("exec_system_reboot")
            time.sleep(20)

        if is_next_day(prev_datetime_local):
            max_elapsed_local_time.replace(day=system_local_time.day)

        write_log("Current time: " + str(get_system_time_utc()))
        time.sleep(LOOP_DELAY_SECOND)

