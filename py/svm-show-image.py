import os
import sys
import time
import tkinter
from tkinter import *
import tkinter.font
import PIL.ImageTk
from PIL import Image, ImageTk

from typing import List, Optional
from threading import Thread
import signal


class ArgData:
    arg: str
    data: str
    is_need_data: bool

    def __init__(self, arg: str, is_need_data: bool, arg_data: str):
        self.arg = arg
        self.data = arg_data
        self.is_need_data = is_need_data

    def set_arg(self, arg: str):
        self.arg = arg

    def set_data(self, arg_data: str):
        self.data = arg_data

    def set_need_data(self, is_need_data: bool):
        self.is_need_data = is_need_data


class SvmShowImage(Thread):
    # Options: {option : need data=True/don't need data=False}
    argument_option = {
        '--file': True,
        '--display': True,
        '--width': True,
        '--height': True,
        '--persistence': False,
        '--help': False,
        '--text': True,
        '--text-x': True,
        '--text-y': True,
        '--text-size': True
    }

    def __init__(self):
        Thread.__init__(self)
        self.img_window: Optional[Tk] = None

    def run(self):
        # Fetch and initial arguments validation
        input_arg: List[ArgData] = []
        current_arg: Optional[ArgData] = None
        for index, arg in enumerate(sys.argv):
            if arg in self.argument_option:
                if current_arg is None:
                    is_need_data = self.argument_option.get(arg)
                    current_arg = ArgData(arg, is_need_data, '')
                    if not is_need_data:
                        input_arg.append(current_arg)
                        current_arg = None
                else:
                    self.exit_error("Error wrong option data " + str(current_arg.arg))
            else:
                if current_arg is not None:
                    if current_arg.is_need_data:
                        current_arg.set_data(arg)
                        input_arg.append(current_arg)
                        current_arg = None
                    else:
                        self.exit_error("Error wrong option data " + str(current_arg.arg))
                else:
                    if index > 0:
                        self.exit_error("Error wrong option data " + str(arg))

        # Incomplete arguments
        if current_arg is not None:
            self.exit_error("Error wrong option data " + str(current_arg.arg))

        # Display input arguments
        # for data in input_arg:
        #     print("arg: ", data.arg)
        #     print("data: ", data.data)
        #     print("is_need_data: ", data.is_need_data)
        #     print("--")

        image_path = ''
        size_width = -1
        size_height = -1
        is_persistence = False
        display = ':0.0'
        user_text = ""
        user_text_x = 0
        user_text_y = 0
        user_text_size = 12

        # Apply arguments
        for arg_data in input_arg:
            if arg_data.arg == '--help':
                self.display_usage()
                self.exit_no_error()
            elif arg_data.arg == '--persistence':
                is_persistence = True
            elif arg_data.arg == '--display':
                display = arg_data.data
                os.environ['DISPLAY'] = display
            elif arg_data.arg == '--file':
                image_path = arg_data.data
            elif arg_data.arg == '--width':
                size_width = arg_data.data
            elif arg_data.arg == '--height':
                size_height = arg_data.data
            elif arg_data.arg == '--text':
                user_text = arg_data.data
            elif arg_data.arg == '--text-x':
                user_text_x = arg_data.data
            elif arg_data.arg == '--text-y':
                user_text_y = arg_data.data
            elif arg_data.arg == '--text-size':
                user_text_size = arg_data.data

        img_window = Tk()
        img_window.bind('<Escape>', self.event_btn_pressed_esc)
        img_window.attributes("-fullscreen", True)

        screen_width = img_window.winfo_screenwidth()
        screen_height = img_window.winfo_screenheight()

        # Keep window on most top
        img_window.wm_attributes("-topmost", True)
        img_window.focus_set()

        img: Optional[PIL.ImageTk.PhotoImage] = None
        canvas: Optional[tkinter.Canvas] = None

        # Load image
        if len(image_path) >= 0:
            try:
                img = self.__open_image(image_path, screen_width, screen_height)
                if size_width == -1:
                    size_width = screen_width

                if size_height == -1:
                    size_height = screen_height

            except Exception as e:
                self.exit_unable_open_image(image_path)
        else:
            self.exit_wrong_image_path()

        if is_persistence:
            img_window.wm_overrideredirect(True)
        else:
            img_window.wm_overrideredirect(False)

        canvas = Canvas(img_window, width=size_width, height=size_height, highlightthickness=0)
        canvas.pack(fill='both')
        canvas.create_image(0, 0, anchor=NW, image=img)

        if len(user_text) > 0:
            text_font = tkinter.font.Font(family='Helvetica', size=user_text_size, weight='bold')
            Canvas.create_text(canvas, user_text_x, user_text_y, text=user_text, font=text_font)

        img_window.mainloop()

    @staticmethod
    def exit_no_error():
        quit(0)

    @staticmethod
    def exit_error(exit_msg: str):
        print(exit_msg)
        quit(1)

    @staticmethod
    def exit_wrong_image_path():
        print("Error wrong image path")
        quit(1)

    @staticmethod
    def exit_unable_open_image(image_path: str):
        print("Error unable to open image ", image_path)
        quit(1)

    @staticmethod
    def display_usage():
        print("====================================================")
        print("                   svm-show-image.py                ")
        print("====================================================")
        print("Usage: svm-show-image.py [options]")
        print("")
        print("Option                          Meaning")
        print("--help                        : Show this help page")
        print("--file [path]                 : Image path (jpg, png format)")
        print("--width [width]               : Image width")
        print("--height [height]             : Image height")
        print("--display [:display]          : Display no")
        print("--persistence                 : Persistence display on most top")
        print("--text [user text]            : User text")
        print("--text-x [text x coordinate]  : User text x coordinate")
        print("--text-y [text y coordinate]  : User text y coordinate")
        print("--text-size [text size]       : User text size")
        print("")

    def event_btn_pressed_esc(self, event):
        # print("event_btn_pressed_esc: ", event)
        if self.img_window is not None:
            self.img_window.destroy()
            self.img_window = None

    def __open_image(self, image_path: str, width=None, height=None) -> PhotoImage:
        if width is not None and height is not None:
            img = Image.open(image_path)
            return ImageTk.PhotoImage(img.resize((width, height), Image.ANTIALIAS))
        else:
            return PhotoImage(file=image_path)


def sigint_handler(sig, frame):
    myApp.img_window.quit()
    myApp.img_window.update()


if __name__ == '__main__':
    myApp = SvmShowImage()
    signal.signal(signal.SIGINT, sigint_handler)
    myApp.start()
