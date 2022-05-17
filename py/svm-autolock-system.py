import os
import time


VERBOSE = False
TIME_INTERVAL_CHECK_ACTIVE_USER = 300
TIME_DELAY_TO_LOCK_SYSTEM = 3600


def any_active_ssh_user() -> bool:
    is_active = False
    response = os.popen('who | grep pts').read()
    if len(response) > 0:
        is_active = True
            
    return is_active
    
    
def any_active_vnc_user() -> bool:
    is_active = False
    response = os.popen('ss -H sport = :5900').read()
    if len(response) > 0:
        is_active = True
            
    return is_active
    

def is_system_locked() -> bool:
    is_locked = False
    response_boot = os.popen('mount | grep mmcblk0p1 | grep ro').read()
    response_rootfs = os.popen('mount | grep mmcblk0p2 | grep ro').read()
    if len(response_boot) > 0 and len(response_rootfs) > 0:
        is_locked = True
        
    return is_locked
    
    
def lock_system():
    os.popen('sudo lock-system').read()
    

if __name__ == '__main__':       
    timer_interval_check_active_user = time.monotonic()
    timer_delay_to_lock_machine = time.monotonic()
    
    is_process_finish = False
    is_locking_system = False
    
    while not is_process_finish:
        if (time.monotonic() - timer_interval_check_active_user) > TIME_INTERVAL_CHECK_ACTIVE_USER:
            if any_active_vnc_user() == False and any_active_ssh_user() == False:
                if not is_locking_system:
                    timer_delay_to_lock_machine = time.monotonic()
                    is_locking_system = True
            else:
                if is_locking_system:
                    is_locking_system = False
            timer_interval_check_active_user = time.monotonic()
           
        if is_locking_system:
            if (time.monotonic() - timer_delay_to_lock_machine) > TIME_DELAY_TO_LOCK_SYSTEM:
                is_process_finish = True
           
        if is_system_locked():
            is_process_finish = True
                               
        time.sleep(5)
    
    lock_system()
    
    
