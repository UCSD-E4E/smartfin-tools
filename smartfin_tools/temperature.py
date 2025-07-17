'''Reference Temperature Sensor
'''
from __future__ import annotations

import datetime as dt
import xml.etree.ElementTree as ET
from abc import abstractmethod
from contextlib import AbstractContextManager
from typing import Any, Optional

import pytz
import serial
from serial.tools.list_ports import comports


class AbstractTemperatureSensor(AbstractContextManager):
    @abstractmethod
    def __init__(self, **kwargs) -> None:
        pass

    @abstractmethod
    def get_temp_C(self) -> float:
        pass

class SBE37 (AbstractTemperatureSensor):
    """This controls the SBE37-SM CTD.

    Reference https://www.seabird.com/moored/sbe-37-sm-smp-smp-odo-microcat/family-downloads?productCategoryId=54627473786
    SBE 37 SM, SMP, SMP-ODO user manual

    """
    def __init__(self, *, port: str, baud: int, **kwargs) -> None:
        if port not in [port.name for port in comports()]:
            raise NameError('Unknown serial port!')
        self.__port_name = port
        self.__baudrate = baud
        self.__port: Optional[serial.Serial] = None
        super().__init__(**kwargs)

    def __enter__(self) -> SBE37:
        self.start()
        return super().__enter__()

    def start(self):
        self.__port = serial.Serial(self.__port_name, baudrate=self.__baudrate)
        self.__port.send_break()
        self.__port.flush()
        self.__port.read_all()

        now = dt.datetime.now(tz=pytz.UTC)
        self.__command('datetime', now.strftime('%m%d%Y%H%M%S'))
        self.__command('OutputFormat', 2) # we want XML output

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()

    def __fflush(self):
        if self.__port is None:
            raise RuntimeError()
        self.__port.read_all()
    def stop(self):
        if self.__port is not None:
            self.__port.close()
        else:
            raise RuntimeError('Exiting closed context')
    def __command(self, cmd: str, param: Optional[Any] = None) -> str:
        if self.__port is None:
            raise RuntimeError('Not opened')
        self.__fflush()
        if param is not None:
            cmd_str = f'{cmd}={param}\r'
        else:
            cmd_str = f'{cmd}\r'
        self.__port.write(cmd_str.encode())
        binary_response = self.__port.read_until(b'<Executed/>')
        response = binary_response.decode()
        lines = response.splitlines()
        return '\n'.join(lines[1:-1])
    
    def get_temp_C(self) -> float:
        response = self.__command('ts')
        root = ET.fromstring(response)
        return float(root.find('./data/t1').text)
