import threading
from typing import List
from .logutils import LogUtils, LogLevel


class StrUtils:
    __lock_from_list_hex = threading.Lock()
    __lock_get_strhex_from_int = threading.Lock()
    __lock_get_str_from_list_int = threading.Lock()
    __lock_get_listint_from_ascii_nibble = threading.Lock()
    __lock_get_str_from_list_ascii = threading.Lock()
    __lock_get_listint_from_strhex = threading.Lock()
    __lock_get_bytearray_from_list_str = threading.Lock()

    @classmethod
    def get_strhex_from_bytearray(cls, list_of_hex: bytearray) -> str:
        cls.__lock_from_list_hex.acquire()
        str_hex = str('{}'.format("".join("{:02x}".format(num).upper() for num in list_of_hex)))
        cls.__lock_from_list_hex.release()
        return str_hex

    @classmethod
    def get_bytearray_from_list_str(cls, list_of_str: List[str]) -> bytearray:
        cls.__lock_get_bytearray_from_list_str.acquire()
        list_of_int: List[int] = []
        for element in list_of_str:
            for char_element in element:
                list_of_int.append(ord(char_element))
        cls.__lock_get_bytearray_from_list_str.release()
        return bytearray(list_of_int)

    @classmethod
    def get_strhex_from_int(cls, value: int, prefix: bool = False, digit: int = 2) -> str:
        cls.__lock_get_strhex_from_int.acquire()
        if prefix:
            # Convert with '0x' prefix infront of the value, e.g: 0x0F
            str_hex = format(value, '0' + str(digit) + 'x').upper()
            str_hex = '0x' + str_hex
        else:
            # No '0x' prefix, e.g: 0F
            str_hex = format(value, '0' + str(digit) + 'x').upper()
        cls.__lock_get_strhex_from_int.release()
        return str_hex

    @classmethod
    def get_strhex_from_list_int(cls, list_of_int: List[int]) -> str:
        cls.__lock_get_str_from_list_int.acquire()
        ret_val = ''
        for val in list_of_int:
            ret_val += '{:02x}'.format(val).upper()
        cls.__lock_get_str_from_list_int.release()
        return ret_val

    # Convert from string_of_hex to List[int]
    # e.g: (input)  strhex: "020602000B02000D0301"
    #      (output) return: List[2, 6, 2, 0, 11, 2, 0, 13, 3, 1]
    @classmethod
    def get_listint_from_strhex(cls, strhex: str) -> List[int]:
        cls.__lock_get_listint_from_strhex.acquire()
        ret_val: List[int] = []

        strhex_len = len(strhex)
        if strhex_len % 2 == 0:
            for index in range(0, strhex_len, 2):
                ret_val.append(int(strhex[index:index + 2], 16))

        else:
            LogUtils.log(cls, LogLevel.DEBUG, "get_listint_from_strhex: Incorrect strhex count")

        cls.__lock_get_listint_from_strhex.release()
        return ret_val

    @classmethod
    def get_listint_from_ascii_nibble(cls, ascii_nibble_data: List[int]) -> List[int]:
        cls.__lock_get_listint_from_ascii_nibble.acquire()
        ret_val = []
        data_len = len(ascii_nibble_data)

        if data_len % 2 == 0:
            i = 0
            # data_len_half = data_len / 2
            data_len_half = data_len
            while i < data_len_half:
                value_msb = ascii_nibble_data[i] - (48 if (ascii_nibble_data[i] < 58) else 55)
                value_lsb = ascii_nibble_data[i + 1] - (48 if (ascii_nibble_data[i + 1] < 58) else 55)
                ret_val.append((value_msb << 4) | (value_lsb))
                i += 2

        cls.__lock_get_listint_from_ascii_nibble.release()
        return ret_val

    @classmethod
    def get_str_from_list_ascii(cls, ascii_data: List[int]) -> str:
        cls.__lock_get_str_from_list_ascii.acquire()
        # LogUtils.log(cls, LogLevel.DEBUG, "ascii_data: " + StrUtils.get_str_from_list_int(ascii_data))
        ret_val = ''.join(chr(data) for data in ascii_data)
        cls.__lock_get_str_from_list_ascii.release()
        # LogUtils.log(cls, LogLevel.DEBUG, "get_str_from_list_ascii: " + ret_val)
        return ret_val

    @classmethod
    def get_int_from_strhex(cls, strhex):
        return int(strhex, 16)
