import time
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import telnetlib

import datetime
import os
import sys

ROUTER_IP_ADDR = "192.168.1.1"
TELNET_USER = "admin"
TELNET_PASSWD = "admin"

ENABLE_DEBUG = False

ROUTER_USB_DEV = "/dev/ttyUSB2"


def get_args() -> list:
    if len(sys.argv) > 1:
        return [sys.argv[1]]
    else:
        return []

def is_router_online(ip_addr: str) -> bool:
    ping_param = '-c 1'
    timeout_param = '-w2'
    output_null_direction = ' > /dev/null 2>&1'

    # Ping remote address
    if os.system('ping ' + ping_param + ' ' + timeout_param + ' ' + ip_addr + output_null_direction) == 0:
        return True
    else:
        return False

def connect(telnet_obj: telnetlib.Telnet, host: str, port: int=0) -> telnetlib.Telnet:
    if is_router_online(host):
        telnet_obj = telnetlib.Telnet(host, port)
        telnet_obj.read_until(b"login: ", timeout=5)
        telnet_obj.write(TELNET_USER.encode('ascii') + b"\n")
        if TELNET_PASSWD:
            telnet_obj.read_until(b"password: ", timeout=5)
            telnet_obj.write(TELNET_PASSWD.encode('ascii') + b"\n")
            telnet_obj.read_until(b"root:~#", timeout=5)

            if ENABLE_DEBUG:
                print("Telnet is connected")

            return telnet_obj
    else:
        # print("Router", ROUTER_IP_ADDR, "is unavailable")
        return None

def disconnect(telnet_obj: telnetlib.Telnet):
    if telnet_obj is not None:
        telnet_obj.write(TELNET_PASSWD.encode('ascii') + b"\n")
        time.sleep(1)

def get_modem_port(telnet_obj: telnetlib.Telnet) -> str:
    MODEM_PORT_LIST = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3"]
    found_port = ""
    for port in MODEM_PORT_LIST:
        telnet_obj.write(("at-cmd " + port + " at+cmgf=1\n").encode('UTF-8'))
        recv_resp = telnet_obj.read_until(b"root:~#", timeout=5).decode('ascii').replace("\r", "").split("\n")
        if len(recv_resp) > 3:
            if recv_resp[3] == "OK":
                found_port = port
                break

    return found_port

def set_sms_mode_text(telnet_obj: telnetlib.Telnet, modem_port: str) -> bool:
    if telnet_obj is not None:
        telnet_obj.write(("at-cmd " + modem_port + " at+cmgf=1\n").encode('UTF-8'))
        recv_resp = telnet_obj.read_until(b"root:~#", timeout=5).decode('ascii').replace("\r", "").split("\n")

        if ENABLE_DEBUG:
            print("len(recv_resp):", len(recv_resp), ":", recv_resp)

        if recv_resp[3] == "OK":
            return True
        else:
            return False
    else:
        print("No connection to server")
        return False

def read_sms_by_index(telnet_obj: telnetlib.Telnet, modem_port: str, read_index) -> list:
    recv_sms = []
    if telnet_obj is not None:
        telnet_obj.write(("at-cmd " + modem_port + " at+cmgr=" + str(read_index) + "\n").encode('UTF-8'))
        recv_resp = telnet_obj.read_until(b"root:~#", timeout=5).decode('ascii').replace("\r", "").split("\n")
        # print("len(recv_resp):", len(recv_resp))
        # for index, ctx in enumerate(recv_resp):
        #     print("recv_resp - ", index, ":", ctx)

        if len(recv_resp) >= 9:
            sms_info = recv_resp[3].replace('"', '').split(",")
            # for index, ctx in enumerate(sms_info):
            #     print("sms_info - ", index, ":", ctx)

            recv_sms.append(datetime.datetime.strptime(sms_info[3] + "_" + sms_info[4].split("+")[0], "%y/%m/%d_%H:%M:%S"))
            recv_sms.append(sms_info[1])
            recv_sms.append(recv_resp[4].strip())
    else:
        print("No connection to server")
    return recv_sms

def read_all_sms(telnet_obj: telnetlib.Telnet, modem_port: str) -> list:
    MAX_READ_CNT = 3
    recv_all_sms = []
    if telnet is not None:
        read_index = 0
        read_cnt = 0
        while True:
            sms_ctx = read_sms_by_index(telnet_obj, modem_port, read_index)
            if len(sms_ctx) > 0:
                read_cnt = 0
                recv_all_sms.append(sms_ctx)
                read_index += 1
            else:
                # Repeat reading the same index
                if read_cnt > MAX_READ_CNT:
                    # If reached max reading attempt, exit function
                    break
                read_cnt += 1
    else:
        print("No connection to server")

    # print("recv_all_sms:", recv_all_sms)
    return recv_all_sms

def delete_all_sms(telnet_obj: telnetlib.Telnet, modem_port: str) -> bool:
    if telnet_obj is not None:
        telnet_obj.write(("at-cmd " + modem_port + " at+cmgd=0,4\n").encode('UTF-8'))
        recv_resp = telnet_obj.read_until(b"root:~#", timeout=5).decode('ascii').replace("\r", "").split("\n")
        # print("len(recv_resp):", len(recv_resp), ":", recv_resp)
        if recv_resp[3] == "OK":
            return True
        else:
            return False
    else:
        print("No connection to server")
        return False

if __name__ == '__main__':
    telnet: telnetlib.Telnet = None
    user_arg = get_args()
    if len(user_arg) > 0:
        telnet = connect(telnet, ROUTER_IP_ADDR)

        if telnet is not None:
            if ENABLE_DEBUG:
                print("user_arg:", user_arg)

            router_modem_port = get_modem_port(telnet)
            if router_modem_port == "":
                print("Unable to find modem port")
                exit()

            if user_arg[0] == "--delete-all-sms":
                if delete_all_sms(telnet, router_modem_port):
                    print("All sms deleted")
                else:
                    print("Failed to delete sms")
            elif user_arg[0] == "--read-all-sms":
                if set_sms_mode_text(telnet, router_modem_port):
                    response = read_all_sms(telnet, router_modem_port)

                    if ENABLE_DEBUG:
                        print("response:", response)

                    if len(response) > 0:
                        print(response)
                    else:
                        print("Sms is empty")
                else:
                    print("Failed to set sms text mode")
            disconnect(telnet)
        else:
            print("Router", ROUTER_IP_ADDR, "is unavailable")
    else:
        pass

    exit()
