import os
import time
import subprocess
import threading
import time
import tkinter
import PIL
from PIL import Image, ImageTk
import sys
import tkinter.font
import tkinter.scrolledtext
from typing import List
import random

VERBOSE = False
IMG_PATH: str = '/opt/svm-tools/py/asset-svm-init-machine/img'
TITLE_TEXT: str = "MOHON TUNGGU"

g_screen_width_ratio = 0
g_screen_height_ratio = 0


class TimerInterval(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class LabelJugglingAnim:
    def __init__(self, parent, title_text: str, x: int, y: int, spacing: int, font_size: int):
        self.char: List[tkinter.Label] = []
        self.x: List[int] = []
        self.y: List[int] = []
        self.y_origin: List[int] = []
        self.y_offset_max: List[int] = []
        self.y_dir: List[int] = []

        __font_title = tkinter.font.Font(family='Fixedsys', size=font_size, weight='normal')
        index = 0
        for title_char in title_text:
            self.char.append(tkinter.Label(parent, text=title_char, borderwidth=0, font=__font_title))
            xpos = x + (index * spacing)
            self.char[len(self.char) - 1].place(x=xpos, y=y)
            self.x.append(xpos)
            self.y.append(y)
            self.y_origin.append(y)
            self.y_offset_max.append(y + random.randint(5, 10))
            dir_val = random.randint(-1, 1)
            if dir_val == 0:
                dir_val = 1
            self.y_dir.append(dir_val)
            index += 1

    def update(self):
        char_count = len(self.char)
        for index in range(0, char_count):
            self.y[index] = self.y[index] + self.y_dir[index]
            if self.y[index] > self.y_offset_max[index]:
                self.y_dir[index] = -1
            elif self.y[index] < self.y_origin[index]:
                self.y_dir[index] = 1
            self.char[index].place(x=self.x[index], y=self.y[index])


anim_title: LabelJugglingAnim
player_title_animation: threading.Timer = None
global_canvas: tkinter.Canvas = None
tk_window = None
cmd_output_textbox: tkinter.Text = None

is_app_completed: bool = False
img_holder = []

img_progressbar_bit: tkinter.PhotoImage = None
img_progressbar_bg: tkinter.PhotoImage = None
progressbar_current_percent: int = 0
progressbar_show_index: List[int] = []

list_db_services: List[str] = \
    [
        'wpa_supplicant.service',
        'openvpn.service',
        'mysql.service',
        'mariadb.service',
    ]

list_all_services: List[str] = \
    [
        'nginx.service',
        'rabbitmq-server.service',
        'rabbit-consumer.service',
        'virtual-tty-relay.service',
        'svm-scheduled-restart.service',
        'pyshake.service',
        'pm2-pi.service'
    ]


def update_cmd_output_textbox(text: str):
    global cmd_output_textbox
    cmd_output_textbox.insert(tkinter.END, text + "\n")
    cmd_output_textbox.see("end")
    print(text)


def start_services(list_of_services: List[str]):
    global g_screen_width_ratio
    global g_screen_height_ratio

    TOTAL_PROGRESS_BAR_ASSIGNED = 20
    single_progress_bar_val = TOTAL_PROGRESS_BAR_ASSIGNED / len(list_of_services)

    for cmd in list_of_services:
        start_retry_cnt = 5
        while start_retry_cnt > 0:
            start_retry_cnt -= 1
            os.popen('sudo systemctl restart ' + cmd).read()
            # Check if the service is started
            is_enabled = os.popen('systemctl is-active ' + cmd).read().strip()
            update_cmd_output_textbox("Starting " + cmd + ": " + is_enabled)

            if is_enabled == 'active':
                update_progressbar(int(single_progress_bar_val), g_screen_width_ratio, g_screen_height_ratio)
                break
            else:
                time.sleep(1)


def stop_services(list_of_services: List[str]):
    global g_screen_width_ratio
    global g_screen_height_ratio

    TOTAL_PROGRESS_BAR_ASSIGNED = 20
    single_progress_bar_val = TOTAL_PROGRESS_BAR_ASSIGNED / len(list_of_services)

    for cmd in list_of_services:
        stop_retry_cnt = 5
        while stop_retry_cnt > 0:
            stop_retry_cnt -= 1
            os.popen('sudo systemctl stop ' + cmd).read()
            # Check if the service is started
            is_enabled = os.popen('systemctl is-active ' + cmd).read().strip()
            update_cmd_output_textbox("Stopping " + cmd)

            if is_enabled == 'inactive' or is_enabled == 'failed':
                update_progressbar(int(single_progress_bar_val), g_screen_width_ratio, g_screen_height_ratio)
                break
            else:
                time.sleep(1)
                

def get_tunnel_address(interface_name: str) -> str:
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


def get_wifi_ssid() -> str:
    wifi_ssid = ''
    try:
        response = os.popen('iwgetid -r').read()
        if len(response) > 0:
            wifi_ssid = response

    except:
        pass

    return wifi_ssid


def is_wifi_tunnel_ready() -> bool:
    success = False
    checking_attempt = 10
    while checking_attempt > 0:
        if len(get_tunnel_address('tun0')) > 0 and len(get_wifi_ssid()) > 0:
            success = True
            break
        checking_attempt -= 1
        time.sleep(5)
    return success


def cmd_purge_then_create_vendingapp_db():
    global g_screen_width_ratio
    global g_screen_height_ratio

    list_db_operations = \
        [
            #'sudo mysql -e "drop database vendingapp"',
            # '[[ -d "/home/pi/.mysql/vendingapp" ]] && rm -rf "/home/pi/.mysql/vendingapp"',
            #'sudo rm -rf "/home/pi/.mysql/vendingapp"',
            #'sudo -u pi /usr/bin/bash -lc "(cd /smartvending/server && rails db:create)"',
            #'sudo -u pi /usr/bin/bash -lc "(cd /smartvending/server && rails db:migrate)"',
            #'sudo -u pi /usr/bin/bash -lc "(cd /smartvending/server && rails db:seed)"',
            'sudo -u pi /usr/bin/bash -lc "(cd /smartvending/server && rails startup:config)"'
        ]

    TOTAL_PROGRESS_BAR_ASSIGNED = 20
    single_progress_bar_val = TOTAL_PROGRESS_BAR_ASSIGNED / len(list_db_operations)
    for cmd in list_db_operations:
        try:
            update_cmd_output_textbox(cmd)
            response = os.popen(cmd).read()
            update_cmd_output_textbox(response.strip())
            
        except Exception as e:
            update_cmd_output_textbox(str(e).strip())

        update_progressbar(int(single_progress_bar_val), g_screen_width_ratio, g_screen_height_ratio)


def create_progressbar(parent, screen_width_ratio: float, screen_height_ratio: float):
    global img_progressbar_bg
    global img_progressbar_bit

    img_progressbar_bg = open_image_with_ratio(IMG_PATH + '/progressbar-bg.jpg', screen_width_ratio, screen_height_ratio)
    img_progressbar_bit = open_image_with_ratio(IMG_PATH + '/progressbar-bit.jpg', screen_width_ratio, screen_height_ratio)
    tkinter.Label(parent, image=img_progressbar_bg, borderwidth=0).place(x=1100/screen_width_ratio, y=130/screen_height_ratio)


def update_progressbar(percentage: int, screen_width_ratio: float, screen_height_ratio: float):
    global img_progressbar_bit
    global progressbar_show_index
    global progressbar_current_percent

    try:
        progressbar_current_percent += percentage

        # Total bar count for 100% is 30
        BAR_COUNT_MAX = 30
        BAR_POSX1 = 1107
        BAR_SPACING = 23

        current_bar_count = int(BAR_COUNT_MAX * progressbar_current_percent / 100)
        for bar_index in range(0, current_bar_count):
            if bar_index not in progressbar_show_index:
                progressbar_show_index.append(bar_index)
                if current_bar_count <= BAR_COUNT_MAX:
                    tkinter.Label(tk_window, image=img_progressbar_bit, borderwidth=0).place(x=(BAR_POSX1 + (BAR_SPACING * bar_index))/screen_width_ratio, y=137/screen_height_ratio)
    except:
        # print_verbose("Exception update_progressbar:", traceback.print_exc())
        pass


def task_main():
    global list_db_services
    global list_all_services
    global g_screen_width_ratio
    global g_screen_height_ratio

    stop_services(list_all_services)
    start_services(list_db_services)

    wifi_tunnel_ready = is_wifi_tunnel_ready()
    update_progressbar(10, g_screen_width_ratio, g_screen_height_ratio)
    print_verbose("Waiting wifi and tunnel: " + str(wifi_tunnel_ready))

    cmd_purge_then_create_vendingapp_db()
    start_services(list_all_services)
    # time.sleep(5)

    # os.popen('sudo systemctl start pm2-pi.service').read()
    print_verbose("task_main exit.")
    update_progressbar(10, g_screen_width_ratio, g_screen_height_ratio)

    exit_gui()


def print_verbose(message1, message2=None, message3=None, message4=None):
    # logfile = open('/tmp/svm-init-machine.log', 'a')
    if VERBOSE:
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

        print(message1_val, message2_val, message3_val, message4_val)
        # logfile.write(message1_val + " " + message2_val + " " + message3_val + " " + message4_val + "\n")
        # logfile.close()


def timer_update_title_animation():
    global anim_title
    anim_title.update()


def start_title_animation():
    global player_title_animation
    player_title_animation = TimerInterval(1 / 10, timer_update_title_animation)
    player_title_animation.start()


def stop_title_animation():
    player_title_animation.cancel()


def event_btn_pressed_esc(event):
    exit_gui()


def sigint_handler(sig, frame):
    exit_gui()


def exit_gui():
    global tk_window
    global is_app_completed

    stop_title_animation()
    is_app_completed = True

    if tk_window is not None:
        tk_window.destroy()


def open_image_with_ratio(image_path: str, width_ratio: float, height_ratio: float) -> PhotoImage:
    img = Image.open(image_path)
    return ImageTk.PhotoImage(img.resize((int(img.width/width_ratio), int(img.height/height_ratio)), Image.ANTIALIAS))


def task_tk_window():
    global tk_window
    global anim_title
    global global_canvas
    global img_holder
    global cmd_output_textbox
    global g_screen_width_ratio
    global g_screen_height_ratio

    BACKGROUND_COLOR = '#D6D6D6'
    WINDOW_DEFAULT_WIDTH = 1920
    WINDOW_DEFAULT_HEIGHT = 1080

    tk_window.attributes("-fullscreen", True)

    screen_width = tk_window.winfo_screenwidth()
    screen_height = tk_window.winfo_screenheight()

    screen_width_ratio = WINDOW_DEFAULT_WIDTH / screen_width
    screen_height_ratio = WINDOW_DEFAULT_HEIGHT / screen_height

    tk_window.geometry(str(screen_width) + 'x' + str(screen_height))
    tk_window.bind('<Escape>', event_btn_pressed_esc)
    tk_window.wm_attributes("-topmost", True)
    # tk_window.wm_overrideredirect(True)
    tk_window.focus_set()

    # img_background = PIL.ImageTk.PhotoImage(file=IMG_PATH + '/background.jpg')
    img_background = open_image_with_ratio(IMG_PATH + '/background.jpg', screen_width_ratio, screen_real_height)
    global_canvas = tkinter.Canvas(tk_window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0, bg=BACKGROUND_COLOR)
    global_canvas.create_image(0, 0, anchor=tkinter.NW, image=img_background)
    global_canvas.place(x=0, y=0)
    img_holder.append(img_background)

    font_cmd_output_textbox = tkinter.font.Font(family='Helvetica', size=int(18/screen_width_ratio))
    cmd_output_textbox = tkinter.scrolledtext.ScrolledText(tk_window, font=font_cmd_output_textbox, height=20/screen_width_ratio, width=50/screen_height_ratio, bg='white')
    cmd_output_textbox.place(x=1100/screen_width_ratio, y=300/screen_height_ratio)

    create_progressbar(global_canvas, screen_width_ratio, screen_height_ratio)

    anim_title = LabelJugglingAnim(global_canvas, TITLE_TEXT, int(1105/screen_width_ratio), int(70/screen_width_ratio), int(60/screen_height_ratio), int(30/screen_width_ratio))
    start_title_animation()

    update_progressbar(10, screen_width_ratio, screen_height_ratio)
    time.sleep(1)


if __name__ == '__main__':
    tk_window = tkinter.Tk()

    print_verbose('Loading task_tk_window...')
    task_tk_window()
    threading.Thread(target=task_main, daemon=True).start()
    tk_window.mainloop()

    print_verbose("svm-init-machine done.")
