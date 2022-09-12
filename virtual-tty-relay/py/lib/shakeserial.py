from .strutils import StrUtils
from typing import Union, List, Optional
import serial
import threading
import time
import sys
import os
import traceback


class ShakeSerial:
    """
    Class: Serial port wrapper with callback function
    """
    def __init__(self):
        self.__serialport: serial.Serial = serial.Serial()
        self.__is_run_task_shakeserial_recv: bool = False
        # When stopping task recv, check this flag to make sure it's already ended properly
        self.__is_run_task_shakeserial_recv_ended: bool = True
        self.__callback_recv_function = None
        self.__run_task_shakeserial_recv: Optional[threading.Thread] = None

    def set_shakeserial_config(self, port: str, baudrate: int) -> None:
        self.__serialport.port = port
        self.__serialport.baudrate = baudrate

        # Default port setting
        self.__serialport.bytesize = 8
        self.__serialport.parity = serial.PARITY_NONE
        self.__serialport.stopbits = 1
        self.__serialport.xonxoff = 0
        self.__serialport.rtscts = False
        self.__serialport.dsrdtr = False
        self.__serialport.timeout = 0
        self.__serialport.writeTimeout = 0
        self.__serialport.write_timeout = 0

    def setup_shakeserial_recv_handler(self, function_handler) -> None:
        self.__callback_recv_function = function_handler

    def start_shakeserial(self) -> bool:
        ret_val = False
        # Only run recv thread once
        if not self.__is_run_task_shakeserial_recv:
            if self._open_shakeserial():
                self._wait_reset_serialport_buffer()
                self.__is_run_task_shakeserial_recv = True
                self.__run_task_shakeserial_recv = threading.Thread(target=self.__task_shakeserial_recv)
                self.__run_task_shakeserial_recv.setDaemon(True)
                self.__run_task_shakeserial_recv.start()

                print(str(self.get_shakeserial_port()) + " opened")
                ret_val = True
            else:
                print("Fail to open " + str(self.get_shakeserial_port()))

        return ret_val

    def stop_shakeserial(self) -> None:
        self.__is_run_task_shakeserial_recv = False

        if self.is_shakeserial_open():
            self._close_shakeserial()
            print(str(self.get_shakeserial_port()) + " closed")

        # Wait until the recv thread ending properly
        while not self.__is_run_task_shakeserial_recv_ended:
            time.sleep(.1)

    def send_shakeserial(self, data_out: Union[List[int], List[str], str, bytearray, int]) -> int:
        # ret_val = -1: sending error
        ret_val = -1
        if self.is_shakeserial_open():
            data_to_serial: Optional[bytearray] = None
            try:
                if isinstance(data_out, list):
                    if len(data_out) > 0:
                        if isinstance(data_out[0], int):
                            data_to_serial = bytearray(data_out)

                        elif isinstance(data_out[0], str):
                            list_int: List[int] = []
                            for element in data_out:
                                list_int.append(StrUtils.get_int_from_strhex(element))

                            if len(list_int) > 0:
                                data_to_serial = bytearray(list_int)

                elif isinstance(data_out, str):
                    data_to_serial = bytearray(data_out, 'utf-8')

                elif isinstance(data_out, bytearray):
                    data_to_serial = data_out

                elif isinstance(data_out, int):
                    data_to_serial = bytearray([data_out])

                if len(data_to_serial) > 0:

                    self.__serialport.flushOutput()
                    ret_val = self.__serialport.write(bytearray(data_to_serial))
                    # print("Send serial: " + StrUtils.get_strhex_from_bytearray(bytearray(data_to_serial)))
                else:
                    print("data_out need to be: List[int], List[str], bytearray, str or int")

            except serial.serialutil.SerialTimeoutException:
                print("send_shakeserial timeout: " + StrUtils.get_strhex_from_bytearray(bytearray(data_to_serial)))

            except:
                print("send_shakeserial: " + str(sys.exc_info()))

        else:
            print("Unable to send data, port is not open")

        return ret_val

    def is_shakeserial_open(self) -> bool:
        return self.__serialport.isOpen()

    def get_shakeserial_port(self) -> str:
        return self.__serialport.portstr

    def get_shakeserial_baudrate(self) -> int:
        return self.__serialport.get_settings()['baudrate']

    def _open_shakeserial(self) -> bool:
        try:
            ret_val = False
            if not self.is_shakeserial_open():
                self.__clear_port_config(self.__serialport.portstr)
                self.__serialport.open()
                # self.__reset_serialport_buffer()
                ret_val = True
            return ret_val
        except:
            # Unable to open serial port
            return False

    def _close_shakeserial(self) -> None:
        if self.__serialport.is_open:
            self.__serialport.close()

    def _wait_reset_serialport_buffer(self) -> None:
        if self.is_shakeserial_open():
            time.sleep(0.1)
            print("Flushing Serial buffer ...")

            # Clearing serial output buffer
            # if self.__serialport.out_waiting > 0:
            self.__serialport.reset_output_buffer()

            # First stage for clearing input buffer
            cleared_input_buffer_len = 0
            while self.__serialport.in_waiting > 0:
                time.sleep(0.005)
                cleared_input_buffer_len += self.__serialport.in_waiting
                self.__serialport.reset_input_buffer()

            # Second stage for clearing input buffer
            clearing_input_buffer = True
            while clearing_input_buffer:
                time.sleep(0.005)
                serial_read_len = len(bytearray(self.__serialport.read_all()))
                if serial_read_len > 0:
                    cleared_input_buffer_len += serial_read_len
                else:
                    clearing_input_buffer = False

            if cleared_input_buffer_len > 0:
                print("Serial input buffer cleared: " + str(cleared_input_buffer_len))

            serial_input_buffer_len = self.__serialport.in_waiting
            if serial_input_buffer_len > 0:
                print("Serial input buffer is not empty: " + str(serial_input_buffer_len))
            else:
                # LogUtils.log(self, LogLevel.DEBUG, "Serial input buffer is empty")
                pass

            serial_output_buffer_len = self.__serialport.out_waiting
            if serial_output_buffer_len > 0:
                print("Serial output buffer is not empty: " + str(serial_output_buffer_len))
            else:
                # LogUtils.log(self, LogLevel.DEBUG, "Serial output buffer is empty")
                pass

    def __clear_port_config(self, port: str) -> None:
        if os.name == 'posix':
            if port is not None and port.lower() != 'auto' and port.lower() != 'none':
                print("Clear port config: " + port)

    def __task_shakeserial_recv(self) -> None:
        self.__is_run_task_shakeserial_recv_ended = False
        try:
            while self.__is_run_task_shakeserial_recv:
                serial_buff = bytearray(self.__serialport.read_all())
                if len(serial_buff) > 0:
                    if self.__callback_recv_function is not None:
                        self.__callback_recv_function(serial_buff)
                time.sleep(.1)
        except Exception as e:
            print("__task_shakeserial_recv: " + str(traceback.format_exc()))

        self.__is_run_task_shakeserial_recv_ended = True
