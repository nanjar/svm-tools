import os
import serial
from lib.button import *

VIRTUAL_BUTTON_PATH = '/var/run/virtualport'
VIRTUAL_BUTTON_PORT_SRC1 = VIRTUAL_BUTTON_PATH + '/' + 'ttyCTRL'

BUTTON_MACHINE_ADDRESS = 0x03
BUTTON_COMMAND_ID = 0x03

is_running: bool = True


def sigint_handler(sig, frame):
    global is_running
    is_running = False


if __name__ == '__main__':
    print("====================================================")
    print("                 virtual-button                     ")
    print("                     HS@2022                        ")
    print("====================================================")
    print("")

    if not os.path.exists(VIRTUAL_BUTTON_PORT_SRC1):
        print("Error: Unable to find virtual port: ", VIRTUAL_BUTTON_PORT_SRC1)
        print("Check if virtual-tty-relay service is started")
        print("\n")
        exit()

    print("Starting virtual button ...")
    print("Make sure to set shakecontroller port to: /var/run/virtualport/ttyVM")

    ser = serial.Serial(VIRTUAL_BUTTON_PORT_SRC1, 38600)
    ser.bytesize = 8
    ser.parity = serial.PARITY_NONE
    ser.stopbits = 1
    ser.xonxoff = 0
    ser.rtscts = False
    ser.dsrdtr = False
    ser.timeout = 0
    ser.writeTimeout = 0
    ser.write_timeout = 0

    while is_running:
        print("")
        print("Button available [1 to 8], [11 to 18], [21 to 28]")
        str_button_no = input("Enter button no to trigger [x for exit]: ")

        # Validate button input
        if str_button_no == 'x' or str_button_no == 'X':
            is_running = False

        else:
            try:
                button_no = int(str_button_no)
                if (button_no >= 1 and button_no <= 8) or (button_no >= 11 and button_no <= 18) or (button_no >= 21 and button_no <= 28):
                    button_message = get_button_frame_data(BUTTON_MACHINE_ADDRESS, BUTTON_COMMAND_ID, button_no)
                    ser.write(button_message)
                else:
                    print("Error: Unknown button, please try again")
            except:
                print("Error: Unknown button, please try again")

    print("Exit program")
    print("")

