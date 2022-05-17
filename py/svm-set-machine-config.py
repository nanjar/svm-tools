import os
import threading
import time
import subprocess
from tkinter import *
import PIL
from PIL import ImageTk
import tkinter.font
import signal
from cryptography.fernet import Fernet
import traceback


class TimerInterval(threading.Timer):
    def run(self):
        try:
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)
        except Exception as e:
            print_verbose("Exception TimerInterval:", str(e))


# Init global var
VERBOSE: bool = False
LANGUAGE: str = 'id'
MAX_USERINPUT_DIGIT_LEN: int = 5
TIME_CHECKING_SVMID = 3.0
TIME_CHECKING_INTERNET = 3.0
TIME_CHECKING_WIFI = 3.0
TIME_CHECKING_TUNNEL_IP = 3.0

VERBOSE_LOGFILE: str = '/home/pi/svm-set-machine-config.log'
INTERNET_URL: str = '8.8.8.8'
IMG_PATH: str = '/opt/svm-tools/py/asset-svm-set-machine-config/img'
GIF_GEAR_ANIME_PATH: str = IMG_PATH + '/gear-anime/'

img_background = None
img_holder = []
buffer_userinput_svmid: str = ''
textbox_userinput_set_svmid: tkinter.Label = None

# {'button_type':[button_obj, image_btn, image_btn_pressed]}
handler_btn_numpad: dict = {}
handler_btn_wifi: dict = {}

handler_label_status_data: dict = {}

img_btn_continue: PhotoImage = None
img_btn_continue_pressed: PhotoImage = None
handler_btn_continue: Button = None

run_task_checking_svmid: bool = True
run_task_checking_tunnel_ip: bool = True
run_task_checking_internet: bool = True
run_task_checking_wifi: bool = True
run_task_set_vmid: bool = True
run_task_set_wifi_profile: bool = True
run_task_gif_gear_player: bool = True

buffer_process_svmid: str = ''
buffer_process_wifi_profile: str = ''

elapse_checking_svmid: float = time.monotonic()
elapse_checking_tunnel_ip: float = time.monotonic()
elapse_checking_internet: float = time.monotonic()
elapse_checking_wifi: float = time.monotonic()

img_gif_anime_frame = []
img_gif_anime_frame_index = 0
gif_gear_anime = None
gif_canvas_img = None
player_gif_gear: threading.Timer = None
tk_window = None

list_all_services = \
[
    'wpa_supplicant.service',
    'openvpn.service',
    'mariadb.service',
    'mysql.service',
    'nginx.service',
    'rabbitmq-server.service',
    'rabbit-consumer.service',
    'virtual-tty-relay.service',
    'pm2-pi.service',
    'pyshake.service'
]


def timer_update_gif_frame():
    global img_gif_anime_frame
    global img_gif_anime_frame_index
    global gif_gear_anime

    # print('timer_update_gif_frame:', img_gif_anime_frame_index)
    frame = img_gif_anime_frame[img_gif_anime_frame_index]
    img_gif_anime_frame_index += 1
    if img_gif_anime_frame_index == 203:
        img_gif_anime_frame_index = 0
    gif_gear_anime.config(image=frame)
    gif_gear_anime.image = frame


def print_verbose(message1, message2=None, message3=None, message4=None):
    global VERBOSE

    if VERBOSE:
        logfile = open(VERBOSE_LOGFILE, 'a')

        if message1 is None:
            message1_val = ''
        else:
            message1_val = str(message1)

        if message2 is None:
            message2_val = ''
        else:
            message2_val = str(message2)

        if message3 is None:
            message3_val = ''
        else:
            message3_val = str(message3)

        if message4 is None:
            message4_val = ''
        else:
            message4_val = str(message4)

        # print(message1_val, message2_val, message3_val, message4_val, logfile)
        logfile.write(message1_val + " " + message2_val + " " + message3_val + " " + message4_val + "\n")
        logfile.close()


def get_hostname() -> str:
    return os.popen('cat /etc/hostname | tr -d " \t\n\r"').read()


def get_ip_address(interface_name: str) -> str:
    ip_address = ''
    try:
        response = os.popen('ifconfig ' + interface_name + ' | grep -w inet').read()
        if len(response) > 0:
            response_parsed = response.split()
            if len(response_parsed) > 1:
                if response_parsed[1].lower() != "error":
                    ip_address = response_parsed[1]
    except:
        pass

    return ip_address


def create_ui_set_vmid(parent: tkinter, window_color: str):
    global img_holder
    global textbox_userinput_set_svmid
    global handler_btn_numpad

    btn_data: dict = {}
    # [button_type] = {[x, y, image_button, image_button_pressed]}
    btn_data['set'] = [510, 260, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-pressed.png')]
    btn_data['1'] = [127, 390, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-1.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-1-pressed.png')]
    btn_data['2'] = [326, 390, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-2.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-2-pressed.png')]
    btn_data['3'] = [525, 390, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-3.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-3-pressed.png')]
    btn_data['4'] = [127, 516, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-4.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-4-pressed.png')]
    btn_data['5'] = [326, 516, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-5.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-5-pressed.png')]
    btn_data['6'] = [525, 516, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-6.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-6-pressed.png')]
    btn_data['7'] = [127, 642, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-7.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-7-pressed.png')]
    btn_data['8'] = [326, 642, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-8.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-8-pressed.png')]
    btn_data['9'] = [525, 642, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-9.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-9-pressed.png')]
    btn_data['0'] = [425, 770, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-0.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-0-pressed.png')]
    btn_data['clear'] = [126, 770, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-clear.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-svmid-numpad-clear-pressed.png')]

    for btn_key in btn_data:
        btn_obj = Button(parent, image=btn_data[btn_key][2], borderwidth=0, activeforeground=window_color, activebackground=window_color)
        btn_obj.place(x=btn_data[btn_key][0], y=btn_data[btn_key][1])
        btn_obj.bind("<ButtonPress>", lambda event, numpad_button_type=btn_key: event_button_numpad_pressed(numpad_button_type))
        btn_obj.bind("<ButtonRelease>", lambda event, numpad_button_type=btn_key: event_button_numpad_released(numpad_button_type))
        handler_btn_numpad[btn_key] = [btn_obj, btn_data[btn_key][2], btn_data[btn_key][3]]

    img_textbox_set_vmid = PhotoImage(file=IMG_PATH + '/textbox-set-vmid.png')
    img_label_set_vmid = PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/label-set-svmid.png')

    Label(parent, image=img_textbox_set_vmid, borderwidth=0, activeforeground=window_color, activebackground=window_color).place(x=130, y=275)
    Label(parent, image=img_label_set_vmid, borderwidth=0, activeforeground=window_color, activebackground=window_color).place(x=130, y=195)

    font_userinput = tkinter.font.Font(family='Helvetica', size=50, weight='bold')
    textbox_userinput_set_svmid = Label(parent, font=font_userinput, text='', borderwidth=0, bg='#FFFFFF')
    textbox_userinput_set_svmid.place(x=170, y=280)

    # Holding image files so it wont be cleaned up by garbage collector
    img_holder.append(img_label_set_vmid)
    img_holder.append(img_textbox_set_vmid)


def create_ui_activate_wifi(parent: tkinter, window_color: str):
    global img_holder
    global handler_btn_wifi

    btn_data: dict = {}
    # [button_type] = {[x, y, image_wifi_on, image_wifi_off, image_wifi_pressed]}
    btn_data['1'] = [900, 260, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-1.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-1.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-1-pressed.png')]
    btn_data['2'] = [1099, 260, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-2.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-2.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-2-pressed.png')]
    btn_data['3'] = [1298, 260, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-3.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-3.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-3-pressed.png')]
    btn_data['4'] = [1497, 260, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-4.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-4.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-4-pressed.png')]
    btn_data['5'] = [900, 386, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-5.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-5.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-5-pressed.png')]
    btn_data['6'] = [1099, 386, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-6.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-6.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-6-pressed.png')]
    btn_data['7'] = [1298, 386, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-7.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-7.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-7-pressed.png')]
    btn_data['8'] = [1497, 386, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-8.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-8.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-8-pressed.png')]
    btn_data['9'] = [900, 512, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-9.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-9.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-9-pressed.png')]
    btn_data['10'] = [1099, 512, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-10.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-10.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-10-pressed.png')]
    btn_data['11'] = [1298, 512, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-11.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-11.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-11-pressed.png')]
    btn_data['12'] = [1497, 512, PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-on-profile-12.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-off-profile-12.png'), PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-set-wifi-profile-12-pressed.png')]

    for btn_key in btn_data:
        btn_obj = Button(parent, image=btn_data[btn_key][3], borderwidth=0, activeforeground=window_color, activebackground=window_color)
        btn_obj.place(x=btn_data[btn_key][0], y=btn_data[btn_key][1])
        btn_obj.bind("<ButtonPress>", lambda event, wifi_button_type=btn_key: event_button_set_wifi_profile_pressed(wifi_button_type))
        btn_obj.bind("<ButtonRelease>", lambda event, wifi_button_type=btn_key: event_button_set_wifi_profile_released(wifi_button_type))
        handler_btn_wifi[btn_key] = [btn_obj, btn_data[btn_key][2], btn_data[btn_key][3], btn_data[btn_key][4]]

    # Label
    img_label_activate_wifi = PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/label-activate-wifi.png')
    tkinter.Label(parent, image=img_label_activate_wifi, borderwidth=0, activeforeground=window_color, activebackground=window_color).place(x=900, y=195)
    img_holder.append(img_label_activate_wifi)


def create_ui_status(parent: tkinter, window_color: str):
    img_label_status = PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/label-status.png')
    Label(parent, image=img_label_status, borderwidth=0, activeforeground=window_color, activebackground=window_color).place(x=900, y=680)

    img_icon_status_success = PhotoImage(file=IMG_PATH + '/icon-success.png')
    img_icon_status_fail = PhotoImage(file=IMG_PATH + '/icon-fail.png')
    font_label_status = tkinter.font.Font(family='Helvetica', size=25, weight='normal')

    icon_status1 = Label(parent, font=font_label_status, image=img_icon_status_fail)
    icon_status1.place(x=900, y=740)
    label_status1 = Label(parent, font=font_label_status, text="SVM id:")
    label_status1.place(x=950, y=743)
    label_status_value1 = Label(parent, font=font_label_status, text="tidak ada")
    label_status_value1.place(x=1090, y=743)

    icon_status2 = Label(parent, font=font_label_status, image=img_icon_status_fail)
    icon_status2.place(x=900, y=780)
    label_status2 = Label(parent, font=font_label_status, text="Koneksi ke wifi:")
    label_status2.place(x=950, y=783)
    label_status_value2 = Label(parent, font=font_label_status, text="tidak ada")
    label_status_value2.place(x=1220, y=783)

    handler_label_status_data['status_val1'] = [icon_status1, img_icon_status_success, img_icon_status_fail, label_status_value1]
    handler_label_status_data['status_val2'] = [icon_status2, img_icon_status_success, img_icon_status_fail, label_status_value2]

    # Holding image files so it wont be cleaned up by garbage collector
    img_holder.append(img_label_status)


def set_button_wifi_state(is_on: bool, wifi_button_type: str):
    for button in handler_btn_wifi:
        btn_data = handler_btn_wifi[button]
        btn_data[0].config(image=btn_data[2])

    btn = handler_btn_wifi[wifi_button_type]
    if is_on:
        btn[0].config(image=btn[1])


def clear_numpad_textbox():
    global buffer_userinput_svmid
    global textbox_userinput_set_svmid

    buffer_userinput_svmid = ''
    textbox_userinput_set_svmid.config(text=buffer_userinput_svmid)


def set_all_button_enable(enabled: bool):
    global handler_btn_continue
    global handler_btn_wifi
    global handler_btn_numpad

    if enabled:
        handler_btn_continue['state'] = 'normal'
        for btn_key in handler_btn_wifi:
            handler_btn_wifi[btn_key][0]['state'] = 'normal'
        for btn_key in handler_btn_numpad:
            handler_btn_numpad[btn_key][0]['state'] = 'normal'
    else:
        handler_btn_continue['state'] = 'disabled'
        for btn_key in handler_btn_wifi:
            handler_btn_wifi[btn_key][0]['state'] = 'disabled'
        for btn_key in handler_btn_numpad:
            handler_btn_numpad[btn_key][0]['state'] = 'disabled'


def event_button_numpad_pressed(numpad_button_type: str):
    global handler_btn_numpad
    try:
        # print('event_button_numpad_pressed: ', numpad_button_type)
        if handler_btn_numpad[numpad_button_type][0]['state'] != 'disabled':
            btn = handler_btn_numpad[numpad_button_type]
            btn[0].config(image=btn[2])

    except:
        pass


def event_button_numpad_released(numpad_button_type: str):
    global MAX_USERINPUT_DIGIT_LEN
    global buffer_userinput_svmid
    global textbox_userinput_set_svmid
    global buffer_process_svmid

    try:
        # print('event_button_numpad_released: ', numpad_button_type)
        if handler_btn_numpad[numpad_button_type][0]['state'] != 'disabled':
            btn = handler_btn_numpad[numpad_button_type]
            btn[0].config(image=btn[1])

            if numpad_button_type == '1' or numpad_button_type == '2' or numpad_button_type == '3' or \
                    numpad_button_type == '4' or numpad_button_type == '5' or numpad_button_type == '6' or \
                    numpad_button_type == '7' or numpad_button_type == '8' or numpad_button_type == '9' or \
                    numpad_button_type == '0':
                if len(buffer_userinput_svmid) <= MAX_USERINPUT_DIGIT_LEN:
                    buffer_userinput_svmid += numpad_button_type
                    textbox_userinput_set_svmid.config(text=buffer_userinput_svmid)
            elif numpad_button_type == 'clear':
                clear_numpad_textbox()
            elif numpad_button_type == 'set':
                buffer_process_svmid = buffer_userinput_svmid
                buffer_userinput_svmid = ''
            else:
                print_verbose('Error: event_button_numpad unknown numpad_button_type: ', numpad_button_type)

    except Exception:
        print_verbose("Exception:", traceback.print_exc())


def event_button_set_wifi_profile_pressed(wifi_button_type: str):
    try:
        # print('event_button_set_wifi_profile_pressed: ', wifi_button_type)
        if handler_btn_wifi[wifi_button_type][0]['state'] != 'disabled':
            btn = handler_btn_wifi[wifi_button_type]
            btn[0].config(image=btn[3])

    except Exception:
        print_verbose("Exception:", traceback.print_exc())


def event_button_set_wifi_profile_released(wifi_button_type: str):
    global handler_btn_wifi
    global buffer_process_wifi_profile

    try:
        # print('event_button_set_wifi_profile_released: ', wifi_button_type)
        if handler_btn_wifi[wifi_button_type][0]['state'] != 'disabled':
            btn = handler_btn_wifi[wifi_button_type]
            btn[0].config(image=btn[2])

            if int(wifi_button_type) >= 1 and int(wifi_button_type) <= 12:
                buffer_process_wifi_profile = wifi_button_type

    except Exception:
        print_verbose("Exception:", traceback.print_exc())


def task_action_button_continue():
    set_all_button_enable(False)
    start_gear_animation()

    # echo 'init id' | sudo tee /boot/state.svm
    os.popen("sudo unlock-system -p all").read()
    os.popen("echo 'init " + LANGUAGE + "' | sudo tee /boot/state.svm").read()

    enable_all_services()
    
    os.popen("sudo systemctl daemon-reload").read()
    os.popen("sync").read()
    os.popen("sudo lock-system").read()

    set_all_button_enable(True)
    stop_gear_animation()

    os.popen("sudo reboot now").read()


def event_button_continue_pressed():
    try:
        global handler_btn_continue
        global img_btn_continue_pressed

        if handler_btn_continue['state'] != 'disabled':
            handler_btn_continue.config(image=img_btn_continue_pressed)

    except:
        pass


def event_button_continue_released():
    global handler_btn_continue
    global img_btn_continue

    try:
        if handler_btn_continue['state'] != 'disabled':
            handler_btn_continue.config(image=img_btn_continue)
            threading.Thread(target=task_action_button_continue).start()
            
    except:
        pass


def enable_all_services():
    global list_all_services

    for cmd in list_all_services:
        enable_retry_cnt = 3
        while enable_retry_cnt > 0:
            os.popen('sudo systemctl enable ' + cmd).read()
            # Check if the service is enabled
            is_enabled = os.popen('systemctl is-enabled ' + cmd).read()
            if is_enabled == 'enabled':
                break
            else:
                time.sleep(3)
            enable_retry_cnt -= 1


def stop_all_services():
    global list_all_services

    for cmd in list_all_services:
        stop_retry_cnt = 3
        while stop_retry_cnt > 0:
            os.popen('sudo systemctl stop ' + cmd).read()
            # Check if the service is already stopped
            is_enabled = os.popen('systemctl is-active ' + cmd).read()
            if is_enabled == 'inactive':
                break
            else:
                time.sleep(3)
            stop_retry_cnt -= 1


def event_btn_pressed_esc(event):
    global tk_window
    global run_task_set_vmid
    global run_task_set_wifi_profile

    stop_gear_animation()
    run_task_set_vmid = False
    run_task_set_wifi_profile = False

    if tk_window is not None:
        tk_window.destroy()


def sigint_handler(sig, frame):
    print_verbose('sigint_handler')
    global tk_window
    global run_task_set_vmid
    global run_task_set_wifi_profile

    stop_gear_animation()
    run_task_set_vmid = False
    run_task_set_wifi_profile = False

    if tk_window is not None:
        tk_window.destroy()


def start_gear_animation():
        threading.Thread(target=task_play_gif_gear, daemon=True).start()


def stop_gear_animation():
    global player_gif_gear
    if player_gif_gear is not None:
        if player_gif_gear.is_alive():
            player_gif_gear.cancel()


def set_vpn(vpn_no: str) -> bool:
    global VERBOSE

    success = False
    VPN_FILE = '/opt/svm-tools/config/vpn/vpn-config.crypt'
    MAPPER = 'vpn-config'

    set_all_button_enable(False)
    start_gear_animation()

    vpn_no = vpn_no.lstrip('0')
    print_verbose("Configuring vpn to SVM" + vpn_no)

    try:
        if os.path.exists(VPN_FILE):

            retry_count = 3
            while retry_count > 0:
                print_verbose("Opening pandora box...")
                response = os.popen('echo -n \'' + (Fernet((os.popen('sudo cat /root/config/random.key').read() + os.popen(
                    'vcgencmd bootloader_config | grep _ORDER').read()).replace('\n', '').encode())
                    .decrypt(
                    'gAAAAABg_vwNyWwp7NsvythrP6KVcxCeHzFCNbn1f-_t0QCPxEaEEE0Yp4-e53NLB_W_xIWyR2LosUxhH6nOTdSmmXt6eBZNOCx'
                    '-e6LBoYgehtaMdZc8DVo='.encode())).decode() + '\' | ' + 'sudo cryptsetup open --type luks ' + VPN_FILE +
                                    ' ' + MAPPER).read()
                if response == "":
                    print_verbose("Success")
                else:
                    print_verbose("Fail: ", response)

                if os.path.exists('/dev/mapper/' + MAPPER):
                    break
                else:
                    print_verbose("Retry...", "(" + str(retry_count) + ")")
                retry_count -= 1

            if os.path.exists('/dev/mapper/' + MAPPER):
                subprocess.run('mkdir /tmp/vpn-config'.split())
                subprocess.run(('sudo mount -o ro /dev/mapper/' + MAPPER + ' /tmp/vpn-config').split())
                if os.path.exists('/tmp/vpn-config/SVM' + vpn_no + '.ovpn'):
                    subprocess.run('sudo unlock-system -p'.split())
                    response = subprocess.run(('sudo cp ' + '/tmp/vpn-config/SVM' + vpn_no + '.ovpn' + ' /etc/openvpn/client.conf').split())
                    print_verbose("Response after applying new vpn config:", str(response))
                    current_hostname = get_hostname()
                    print_verbose('Updating hostname from ' + current_hostname + ' to SVM' + vpn_no)
                    os.popen('sudo bash -c "echo SVM' + vpn_no + ' > /etc/hostname"').read()
                    subprocess.run('cp /etc/hosts /tmp/'.split())
                    response = os.popen('sed -i "s/' + current_hostname + '/SVM' + vpn_no + '/g"' + ' /tmp/hosts').read()

                    if response == "":
                        print_verbose("Updating hosts is completed")
                    else:
                        print_verbose("Fail when updating hosts: ", response)

                    subprocess.run('sudo cp /tmp/hosts /etc/'.split())
                    success = True

                    print_verbose("Changing vpn done")

                else:
                    print_verbose("Error unable to find config for SVM" + vpn_no)

            else:
                print_verbose("Error /dev/mapper/", MAPPER, " not found")

        else:
            print_verbose("Error ", VPN_FILE, " not found")

        subprocess.run('sudo umount /tmp/vpn-config'.split())
        subprocess.run('sudo cryptsetup close vpn-config'.split())
        subprocess.run('sudo rm -Rf /tmp/vpn-config'.split())
        subprocess.run('sudo lock-system'.split())

    except Exception:
        print_verbose("Exception:", traceback.print_exc())

    set_all_button_enable(True)
    clear_numpad_textbox()
    stop_gear_animation()
    return success


def remove_wpa() -> bool:
    # Always success :)
    success = True
    try:
        set_all_button_enable(False)
        start_gear_animation()
        if os.path.exists('/etc/wpa_supplicant/wpa_supplicant.conf'):
            subprocess.run('sudo unlock-system -p'.split())
            subprocess.run('sudo rm /etc/wpa_supplicant/wpa_supplicant.conf'.split())
            subprocess.run('sudo lock-system'.split())
        
    except Exception as e:
        print_verbose("Exception remove_wpa:", str(e))

    # Button profile to remove wpa config is always button no 12
    set_button_wifi_state(True, '12')
    set_all_button_enable(True)
    stop_gear_animation()
    return success
    
        
def set_wpa(wpa_no: str) -> bool:
    success = False
    try:
        WPA_FILE = '/opt/svm-tools/config/wpa/wpa-config.crypt'
        MAPPER = 'wpa-config'

        set_all_button_enable(False)
        start_gear_animation()
        if os.path.exists(WPA_FILE):
            retry_count = 3
            while retry_count > 0:
                set_button_wifi_state(True, wpa_no)
                os.popen(
                    'echo -n \'' + (Fernet((os.popen('sudo cat /root/config/random.key').read() + os.popen(
                        'vcgencmd bootloader_config | grep _ORDER').read()).replace('\n', '').encode())
                        .decrypt(
                        'gAAAAABg_xH3sDfeu1Ia9'
                        '-DVrIlFC2V6liRAnUtsRTUhdJO8im9tFVI2qtUOJG4S1cVgvk7p3mEvk8MlM_FMUokSj8kVYthQHGzvGGNKgMmqnwoh6oshiL4'
                        '='.encode())).decode() + '\' | ' + 'sudo cryptsetup open --type luks ' + WPA_FILE + ' ' +
                    MAPPER).read()

                if os.path.exists('/dev/mapper/' + MAPPER):
                    break
                else:
                    print_verbose("Retry...", "(" + str(retry_count) + ")")
                retry_count -= 1

            if os.path.exists('/dev/mapper/' + MAPPER):
                subprocess.run('mkdir /tmp/wpa-config'.split())
                subprocess.run(('sudo mount -o ro /dev/mapper/' + MAPPER + ' /tmp/wpa-config').split())
                if os.path.exists('/tmp/wpa-config/profile' + wpa_no + '.conf'):
                    subprocess.run('sudo unlock-system -p'.split())
                    subprocess.run(('sudo cp ' + '/tmp/wpa-config/profile' + wpa_no + '.conf' + ' /etc/wpa_supplicant/wpa_supplicant.conf').split())
                    success = True
                else:
                    print_verbose("Failed to find wpa profile:", wpa_no)
            else:
                print_verbose("Failed to open wpa storage")

        subprocess.run('sudo umount /tmp/wpa-config'.split())
        subprocess.run('sudo cryptsetup close wpa-config'.split())
        subprocess.run('sudo rm -Rf /tmp/wpa-config'.split())
        subprocess.run('sudo lock-system'.split())

    except Exception as e:
        print_verbose("Exception set_wpa:", str(e))

    if not success:
        set_button_wifi_state(False, wpa_no)

    set_all_button_enable(True)
    stop_gear_animation()
    return success


def task_set_svm_id():
    global buffer_process_svmid
    global run_task_set_vmid

    while run_task_set_vmid:
        if len(buffer_process_svmid) > 0:
            if set_vpn(buffer_process_svmid):
                buffer_process_svmid = ''
            else:
                buffer_process_svmid = ''
        time.sleep(1)


def task_set_wifi_profile():
    global buffer_process_wifi_profile
    global run_task_set_wifi_profile

    while run_task_set_wifi_profile:
        if len(buffer_process_wifi_profile) > 0:
            status2 = handler_label_status_data['status_val2']
            if buffer_process_wifi_profile == '12':
                remove_wpa()
                # Set wifi is not available status
                status2[0].config(image=status2[2])
                status2[3].config(text='tidak ada')
            else:
                if set_wpa(buffer_process_wifi_profile):
                    status2[0].config(image=status2[1])
                    status2[3].config(text='Profile ' + buffer_process_wifi_profile)

                else:
                    # Failed to change wifi profile
                    status2[0].config(image=status2[2])
                    status2[3].config(text='tidak ada')
                    set_button_wifi_state(False, '')
                    
            buffer_process_wifi_profile = ''

        time.sleep(1)


def task_check_svmid():
    global elapse_checking_svmid
    global run_task_checking_svmid
    global handler_label_status_data

    while run_task_checking_svmid:
        if time.monotonic() - elapse_checking_svmid > TIME_CHECKING_SVMID:
            svmid = get_hostname()
            if len(svmid) > 0:
                status1 = handler_label_status_data['status_val1']
                if svmid != 'SVM':
                    status1[0].config(image=status1[1])
                    status1[3].config(text=svmid)
                else:
                    status1[0].config(image=status1[2])
                    status1[3].config(text='tidak ada')

                    print_verbose("SVMId:", svmid)

            elapse_checking_svmid = time.monotonic()
        else:
            time.sleep(2)


def task_check_tunnel():
    global elapse_checking_tunnel_ip
    global run_task_checking_tunnel_ip
    global handler_label_status_data

    while run_task_checking_tunnel_ip:
        if time.monotonic() - elapse_checking_tunnel_ip > TIME_CHECKING_TUNNEL_IP:
            tunnel_ip = get_ip_address('tun0')
            status2 = handler_label_status_data['status_val2']
            if len(tunnel_ip) > 0:
                status2[0].config(image=status2[1])
                status2[3].config(text=tunnel_ip)
            else:
                status2[0].config(image=status2[2])
                status2[3].config(text='tidak ada')
            print_verbose("Tunnel Ip:", tunnel_ip)
            elapse_checking_tunnel_ip = time.monotonic()
        else:
            time.sleep(2)


def task_check_internet():
    global elapse_checking_internet
    global run_task_checking_internet
    global handler_label_status_data

    while run_task_checking_internet:
        if time.monotonic() - elapse_checking_internet > TIME_CHECKING_INTERNET:
            status3 = handler_label_status_data['status_val3']
            try:
                response = os.system("ping -c 1 -w2 " + INTERNET_URL + " > /dev/null 2>&1")
                if response == 0:
                    status3[0].config(image=status3[1])
                    status3[3].config(text='Ok')
                else:
                    status3[0].config(image=status3[2])
                    status3[3].config(text='tidak ada')

                print_verbose("Connection to server:", str(response))

            except:
                print_verbose("Connection to server failed")
                status3[0].config(image=status3[2])
                status3[3].config(text='tidak ada')

            elapse_checking_internet = time.monotonic()
        else:
            time.sleep(2)


def task_check_wifi_connection():
    global elapse_checking_wifi
    global run_task_checking_wifi
    global handler_label_status_data

    while run_task_checking_wifi:
        if time.monotonic() - elapse_checking_wifi > TIME_CHECKING_WIFI:
            process = subprocess.Popen('iwgetid -r'.split(), stdout=subprocess.PIPE)
            out, err = process.communicate()
            wifi_ssid = out.strip().decode()
            status4 = handler_label_status_data['status_val4']
            if len(wifi_ssid) > 0:
                status4[0].config(image=status4[1])
                status4[3].config(text='Ok')
            else:
                status4[0].config(image=status4[2])
                status4[3].config(text='tidak ada')

            print_verbose('Wifi ssid:', wifi_ssid)

            elapse_checking_wifi = time.monotonic()
        else:
            time.sleep(2)


def task_tk_window():
    global tk_window
    global img_background
    global img_holder
    global textbox_userinput_set_svmid
    global img_btn_continue
    global img_btn_continue_pressed
    global handler_btn_continue
    global img_gif_anime_frame
    global gif_gear_anime
    global gif_canvas_img
    
    BACKGROUND_COLOR = '#D6D6D6'
    WINDOW_WIDTH = '1920'
    WINDOW_HEIGHT = '1080'

    tk_window.geometry(WINDOW_WIDTH + 'x' + WINDOW_HEIGHT)
    tk_window.bind('<Escape>', event_btn_pressed_esc)
    tk_window.attributes("-fullscreen", True)
    tk_window.wm_attributes("-topmost", True)
    tk_window.wm_overrideredirect(True)
    tk_window.focus_set()

    img_background = PhotoImage(file=IMG_PATH + '/background.png')
    canvas = tkinter.Canvas(tk_window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0, bg=BACKGROUND_COLOR)
    canvas.create_image(0, 0, anchor=NW, image=img_background)
    canvas.place(x=0, y=0)

    img_label_title_configuration = PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/label-title-configuration.png')
    Label(canvas, image=img_label_title_configuration, borderwidth=0, activeforeground=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR).place(x=706, y=65)

    img_btn_continue = PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-page-continue.png')
    img_btn_continue_pressed = PhotoImage(file=IMG_PATH + '/' + LANGUAGE + '/btn-page-continue-pressed.png')
    handler_btn_continue = Button(canvas, image=img_btn_continue, borderwidth=0, activeforeground=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR)
    handler_btn_continue.place(x=1600, y=30)

    handler_btn_continue.bind("<ButtonPress>", lambda event: event_button_continue_pressed())
    handler_btn_continue.bind("<ButtonRelease>", lambda event: event_button_continue_released())

    create_ui_set_vmid(canvas, BACKGROUND_COLOR)
    create_ui_activate_wifi(canvas, BACKGROUND_COLOR)
    create_ui_status(canvas, BACKGROUND_COLOR)

    signal.signal(signal.SIGINT, sigint_handler)

    for frame in range(1, 204):
        img_gif_anime_frame.append(PIL.ImageTk.PhotoImage(file=GIF_GEAR_ANIME_PATH + '%04d.png' % frame, format='png'))

    gif_gear_anime = Label(canvas, image=img_gif_anime_frame[img_gif_anime_frame_index], borderwidth=0)
    gif_gear_anime.place(x=1450, y=670)


def task_play_gif_gear():
    global player_gif_gear

    player_gif_gear = TimerInterval(1 / 24, timer_update_gif_frame)
    player_gif_gear.start()


if __name__ == '__main__':
    tk_window = Tk()

    print_verbose('Loading task_tk_window...')
    task_tk_window()

    print_verbose('Loading task_set_svm_id...')
    threading.Thread(target=task_set_svm_id, daemon=True).start()

    print_verbose('Loading task_set_wifi_profile...')
    threading.Thread(target=task_set_wifi_profile, daemon=True).start()

    print_verbose('Loading task_check_svmid...')
    threading.Thread(target=task_check_svmid, daemon=True).start()

    tk_window.mainloop()

    print("svm-set-machine-config exit.")
