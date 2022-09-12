import os
import pty
import serial
import threading
import time
import tty
import termios
import queue

# Comm direction: shakecontroller <=> src0 <=> tty <=> device
#                 virtual_button   -> src1  -> src0 (emulate button event from machine) -> shakecontroller

TTYUSB0_PORT = '/dev/ttyUSB0'
TTYUSB1_PORT = '/dev/ttyUSB1'
TTYS0_PORT = '/dev/ttyS0'

VIRTUAL_BUTTON_PATH = '/var/run/virtualport'
VIRTUAL_BUTTON_PORT_SRC0 = VIRTUAL_BUTTON_PATH + '/' + 'ttyVM'
VIRTUAL_BUTTON_PORT_SRC1 = VIRTUAL_BUTTON_PATH + '/' + 'ttyCTRL'

is_running: bool = False
qbuffer_recv_tty_sr1 = queue.Queue()


def onrecv_src0(__virtual_tty, __tty: serial.Serial):
    global is_running
    while is_running:
        __virtual_tty_incoming = os.read(__virtual_tty, 1000)
        if __virtual_tty_incoming is not None and len(__virtual_tty_incoming) > 0:
            __tty.write(__virtual_tty_incoming)
            # print("onrecv_src0:", ''.join(format(my_int, '02X') for my_int in __virtual_tty_incoming))
        time.sleep(0.3)


def onrecv_src1(__virtual_tty):
    global is_running
    while is_running:
        __virtual_tty_incoming = os.read(__virtual_tty, 1000)
        if __virtual_tty_incoming is not None and len(__virtual_tty_incoming) > 0:
            # print("onrecv_src1:", ''.join(format(my_int, '02X') for my_int in __virtual_tty_incoming))
            qbuffer_recv_tty_sr1.put_nowait(__virtual_tty_incoming)
        time.sleep(0.3)


def onrecv_tty_port(__tty: serial.Serial):
    global is_running
    while is_running:
        try:
            if __tty.in_waiting > 0:
                __tty_incoming = __tty.read(30)
                if __tty_incoming is not None and len(__tty_incoming) > 0:
                    # print("onrecv_tty_port:", ''.join(format(my_int, '02X') for my_int in __tty_incoming))
                    qbuffer_recv_tty_sr1.put_nowait(__tty_incoming)
        except:
            pass
        time.sleep(0.3)


def sigint_handler(sig, frame):
    global is_running
    is_running = False


if __name__ == '__main__':
    master_src0, slave_src0 = pty.openpty()
    virtual_tty0 = os.ttyname(slave_src0)
    tty.setraw(master_src0, termios.TCSANOW)

    master_src1, slave_src1 = pty.openpty()
    virtual_tty1 = os.ttyname(slave_src1)
    tty.setraw(master_src1, termios.TCSANOW)

    if not os.path.isdir(VIRTUAL_BUTTON_PATH):
        os.popen('sudo mkdir' + ' ' + VIRTUAL_BUTTON_PATH).read()
        os.popen('sudo chmod 777 -R' + ' ' + VIRTUAL_BUTTON_PATH).read()

    if os.path.islink(VIRTUAL_BUTTON_PORT_SRC0) or os.path.exists(VIRTUAL_BUTTON_PORT_SRC0):
        os.popen('ln -sf' + ' ' + virtual_tty0 + ' ' + VIRTUAL_BUTTON_PORT_SRC0).read()
    else:
        os.popen('ln -s' + ' ' + virtual_tty0 + ' ' + VIRTUAL_BUTTON_PORT_SRC0).read()

    if os.path.islink(VIRTUAL_BUTTON_PORT_SRC1) or os.path.exists(VIRTUAL_BUTTON_PORT_SRC1):
        os.popen('ln -sf' + ' ' + virtual_tty1 + ' ' + VIRTUAL_BUTTON_PORT_SRC1).read()
    else:
        os.popen('ln -s' + ' ' + virtual_tty1 + ' ' + VIRTUAL_BUTTON_PORT_SRC1).read()

    if os.path.exists(TTYUSB0_PORT):
        TTY_PORT = TTYUSB0_PORT
    else:
        if os.path.exists(TTYUSB1_PORT):
            TTY_PORT = TTYUSB1_PORT
        else:
            TTY_PORT = TTYS0_PORT

    ser = serial.Serial(TTY_PORT, 38600)
    ser.bytesize = 8
    ser.parity = serial.PARITY_NONE
    ser.stopbits = 1
    ser.xonxoff = 0
    ser.rtscts = False
    ser.dsrdtr = False
    ser.timeout = 0.05
    ser.writeTimeout = 0
    ser.write_timeout = 0

    is_running = True
    threading.Thread(target=onrecv_src0, args=[master_src0, ser], daemon=True).start()
    threading.Thread(target=onrecv_src1, args=[master_src1], daemon=True).start()
    threading.Thread(target=onrecv_tty_port, args=[ser], daemon=True).start()

    while is_running:
        if qbuffer_recv_tty_sr1.qsize() > 0:
            buffer_out = qbuffer_recv_tty_sr1.get_nowait()
            # print("to master_src0:", ''.join(format(my_int, '02X') for my_int in buffer_out))
            os.write(master_src0, buffer_out)
        time.sleep(0.5)
