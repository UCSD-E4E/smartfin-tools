'''Common definitions
'''
from enum import Enum
from pathlib import Path
from typing import Protocol


class Encoding(Enum):
    """Record encodings
    """
    BASE85 = 'base85'
    BASE64 = 'base64'
    BASE64URL = 'base64url'

    def __str__(self) -> str:
        return self.value


class FileFormats(Enum):
    """File formats (and extensions)
    """
    SFP = '.sfp'
    SFR = '.sfr'
    CSV = '.csv'


class ConverterType(Protocol):
    """Converter function protocol
    """
    # pylint: disable=too-few-public-methods
    # Protocol specification
    def __call__(self, input_path: Path, output_path: Path) -> None:
        pass
