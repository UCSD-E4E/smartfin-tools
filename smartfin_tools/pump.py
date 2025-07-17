'''Thermal Pump Abstraction
'''
from __future__ import annotations

import struct
import time
from abc import abstractmethod
from contextlib import AbstractContextManager
from typing import Any, Dict, Optional, Tuple

import serial
import serial.tools
import serial.tools.list_ports


class AbstractPump(AbstractContextManager):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def set_flow_lpm(self, flow: float) -> None:
        pass

    @abstractmethod
    def get_flow_lpm(self) -> float:
        pass

    @abstractmethod
    def set_temp_C(self, temp: float) -> None:
        pass

    @abstractmethod
    def get_temp_C(self) -> float:
        pass

    @abstractmethod
    def update_config(self, config: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def turn_off(self) -> None:
        pass

    @abstractmethod
    def turn_on(self) -> None:
        pass


class RTE7Pump(AbstractPump):
    """Thermo Scientific RTE 7

    See user manual at https://www.nist.gov/system/files/documents/ncnr/Circulating-Bath_Thermo-Scientific_NESLAB-RTE-7.pdf

    Note that the RTE 7 must be turned on in computer mode.
    1. Turn on the bath
    2. Press and hold the computer button for 5 seconds.  The controller will display `SErL`
    3. Use the UP and DOWN keys to select `232` for RS232.
    4. Press the Computer button to hold the protocol.  The controller will now allow selecting the baud rate.
    5. Use the UP and DOWN keys to select the appropriate baud rate (generally 19200).
    6. Press the Computer button to hold the baud rate.
    7. Press the Computer button to select `StorE`.
    8. Press the YES button to store the config.
    9. Short press the computer button to enable serial interface

    """
    def __init__(self, *, port: str, baud: int, **kwargs):
        if port not in [port.name for port in serial.tools.list_ports.comports()]:
            raise NameError('Unknown serial port!')
        self.__port_name = port
        self.__baudrate = baud
        self.__port: Optional[serial.Serial] = None
        self.__wait_time = 0.01
        super().__init__(**kwargs)

    def __enter__(self) -> RTE7Pump:
        self.start()
        return super().__enter__()

    def start(self):
        self.__port = serial.Serial(self.__port_name, baudrate=self.__baudrate)
        self.__port.flush()
        self.__port.read_all()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()

    def stop(self):
        if self.__port is not None:
            self.__port.close()
        else:
            raise RuntimeError('Exiting closed context')

    def __compute_cksum(self, msg: bytes) -> bytes:
        byte_sum = sum(msg[1:]) & 0x00FF
        return (byte_sum ^ 0xFF).to_bytes(length=1)
    
    def __fflush(self):
        if self.__port is None:
            raise RuntimeError()
        self.__port.read_all()

    def __read_response(self) -> Tuple[bytes, int, int, int, bytes, int]:
        """Reads and parses the response from the pump

        Raises:
            RuntimeError: Uninitialized port

        Returns:
            Tuple: Key byte, address, command byte, payload length, payload,
            checksum
        """
        if self.__port is None:
            raise RuntimeError()
        self.__port.read_until(b'\xca')
        response = b'\xca'
        response += self.__port.read(4)
        n_bytes = response[-1]
        response += self.__port.read(n_bytes + 1)
        retval = struct.unpack(
            f'>cHBB{n_bytes}sB',
            response
        )
        assert response[-1:] == self.__compute_cksum(response[:-1])
        return retval


    def set_temp_C(self, temp: float) -> None:
        if self.__port is None:
            raise RuntimeError('Not opened')
        self.__fflush()
        command = b'\xca\x00\x01\xf0\x02'
        command += struct.pack('>h', int(temp * 10))
        command += self.__compute_cksum(command)
        self.__port.write(command)
        time.sleep(self.__wait_time)
        _, addr, cmd, n_bytes, payload, _ = self.__read_response()
        assert addr == 0x0001
        assert cmd == 0xF0, f'Expected 0xF0, got 0x{cmd:02X}'
        assert n_bytes == 3
        qb, raw_val = struct.unpack('>Bh', payload)
        if qb == 0x11:
            assert raw_val * 0.1 == temp
        elif qb == 0x21:
            assert raw_val * 0.01 == temp

    def get_temp_C(self) -> float:
        if self.__port is None:
            raise RuntimeError('Not opened')
        self.__fflush()
        command = b'\xca\x00\x01\x70\x00\x8e'
        command += self.__compute_cksum(command)
        self.__port.write(command)
        time.sleep(self.__wait_time)
        _, addr, cmd, n_bytes, payload, _ = self.__read_response()
        assert addr == 0x0001
        assert cmd == 0x70
        assert n_bytes == 3
        qb, raw_val = struct.unpack('>Bh', payload)
        if qb == 0x11:
            return raw_val * 0.1
        if qb == 0x21:
            return raw_val * 0.01
        raise RuntimeError('Unknown qb')
    
    def set_flow_lpm(self, flow: float) -> None:
        raise NotImplementedError
    
    def get_flow_lpm(self) -> float:
        raise NotImplementedError


    def get_config(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    def update_config(self, config: Dict[str, Any]) -> None:
        raise NotImplementedError

    def turn_off(self) -> None:
        if self.__port is None:
            raise RuntimeError()
        self.__fflush()
        command = b'\xca\x00\x01\x81\x08\x00\x00\x01\x00\x00\x00\x01\x02'
        command += self.__compute_cksum(command)
        self.__port.write(command)
        time.sleep(self.__wait_time)
        self.__read_response()
    
    def turn_on(self) -> None:
        if self.__port is None:
            raise RuntimeError()
        self.__fflush()
        command = b'\xca\x00\x01\x81\x08\x01\x00\x01\x00\x00\x00\x01\x02'
        command += self.__compute_cksum(command)
        self.__port.write(command)
        time.sleep(self.__wait_time)
        self.__read_response()