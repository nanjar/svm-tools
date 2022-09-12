from logging.handlers import TimedRotatingFileHandler
from logging.handlers import DatagramHandler

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from datetime import timedelta
from datetime import timezone

import logging
import time
import threading
import sys
import os


@dataclass
class LogLevel:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogUtils:
    __logger = None
    __log_format = None
    __lock_log = threading.Lock()
    __log_filter: List[str] = ['']

    @classmethod
    def setup(cls, str_log_level: str) -> None:
        # Insert any string to be filtered on log
        cls.__log_filter = []

        cls.__log_format = logging.Formatter('%(message)s')
        cls.__logger = logging.getLogger(__name__)
        cls.__logger.setLevel(cls.__get_log_level(str_log_level))

    @classmethod
    def setup_file_log(cls, enable: bool, log_filepath: str, log_filename: str):
        # cls.__filelog_enable = enable
        if enable:
            # If path doesn't exist, create it
            if not os.path.exists(log_filepath):
                os.mkdir(log_filepath)

            filename = log_filepath + os.path.sep + log_filename
            log_handler = TimedRotatingFileHandler(filename, when='midnight', backupCount=90)
            log_handler.suffix = "%Y%m%d"
            log_handler.setFormatter(cls.__log_format)
            cls.__logger.addHandler(log_handler)

    @classmethod
    def setup_udp_log(cls, enable: bool, host: str, port: int):
        if enable:
            udplog_handler = UdpHandler(host, port)
            udplog_handler.setFormatter(cls.__log_format)
            cls.__logger.addHandler(udplog_handler)

    @classmethod
    def log(cls, caller, log_level: LogLevel, log_text) -> None:
        # Filter unwanted log_text
        if log_text not in cls.__log_filter:
            if isinstance(log_text, str):
                run_log = threading.Thread(target=cls.__run_log, args=(caller, log_level, log_text))
                run_log.start()
            else:
                run_log = threading.Thread(target=cls.__run_log, args=(caller, LogLevel.ERROR, 'Wrong log_type or log_text datatype'))
                run_log.start()

    @classmethod
    def __get_log_level(cls, str_log_level: str) -> LogLevel:
        log_level = LogLevel.DEBUG
        if str_log_level.upper() == 'INFO':
            log_level = LogLevel.INFO
        elif str_log_level.upper() == 'WARNING':
            log_level = LogLevel.WARNING
        elif str_log_level.upper() == 'ERROR':
            log_level = LogLevel.ERROR
        elif str_log_level.upper() == 'CRITICAL':
            log_level = LogLevel.CRITICAL
        return log_level

    @classmethod
    def __get_str_log_level(cls, log_level: LogLevel) -> str:
        str_log_level = 'DEBUG'
        if log_level == LogLevel.INFO:
            str_log_level = 'INFO'
        elif log_level == LogLevel.WARNING:
            str_log_level = 'WARNING'
        elif log_level == LogLevel.ERROR:
            str_log_level = 'ERROR'
        elif log_level == LogLevel.CRITICAL:
            str_log_level = 'CRITICAL'
        return str_log_level

    @classmethod
    def __format_log(cls, caller, log_level: LogLevel, log_text) -> str:
        current_datetime = str(datetime.now(cls.__system_tz()).isoformat(sep=' ', timespec='milliseconds'))
        text = current_datetime + ' [' + cls.__get_str_log_level(log_level) + ']: ' + "[" + caller.__class__.__name__ + "] " + log_text
        return text

    @classmethod
    def __run_log(cls, caller, log_level: LogLevel, log_text) -> None:
        cls.__lock_log.acquire()
        text = cls.__format_log(caller, log_level, log_text)
        cls.__logger.log(log_level, text)
        cls.__lock_log.release()

    @classmethod
    def __system_tz(cls):
        if time.daylight:
            return timezone(timedelta(seconds=-time.altzone), time.tzname[1])
        else:
            return timezone(timedelta(seconds=-time.timezone), time.tzname[0])

    @classmethod
    def setup_console_log(cls, enable: bool):
        # cls.__console_enable = enable
        if enable:
            consolelog_handler = logging.StreamHandler(sys.stdout)
            consolelog_handler.setFormatter(cls.__log_format)
            cls.__logger.addHandler(consolelog_handler)


class UdpHandler(DatagramHandler):
    def __init__(self, host: str, port: Optional[int]):
        super().__init__(host, port)

    def emit(self, record: logging.LogRecord):
        try:
            self.send(str.encode(record.getMessage() + os.linesep))
        except Exception:
            self.handleError(record)
