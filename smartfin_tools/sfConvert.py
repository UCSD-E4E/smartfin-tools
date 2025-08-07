'''Smartfin Data Conversion
'''
import base64
import shutil
from argparse import ArgumentParser
from base64 import urlsafe_b64decode
from pathlib import Path
from typing import Callable, Dict, Tuple

import pandas as pd

import smartfin_tools.decoder as scd
from smartfin_tools import __version__
from smartfin_tools.common import ConverterType, Encoding, FileFormats
from smartfin_tools.config import configure_logging


def sfr_to_sfp(input_path: Path,
               output_path: Path,
               *,
               strip_padding: bool = False,
               decoder: Callable[[str], bytes] = urlsafe_b64decode):
    """Converts Smartfin Records to Smartfin Packets (base64url to binary)

    Args:
        input_path (Path): Input path
        output_path (Path): Output path
        strip_padding (bool, optional): Flag to strip partial ensembles. 
        Defaults to False.
        decoder (Callable[[str], bytes], optional): Record Ascii to binary 
        decoder. Defaults to urlsafe_b64decode.
    """
    with open(input_path, 'r', encoding='utf-8') as sfr:
        with open(output_path, 'wb') as sfp:
            for record in sfr:
                packet = decoder(record.strip())
                if strip_padding:
                    packet = scd.strip_padding(packet)
                sfp.write(packet)


def sfr_to_csv(in_sfr: Path,
               out_csv: Path,
               *,
               decoder: Callable[[str], bytes] = urlsafe_b64decode):
    data = b''
    with open(in_sfr, 'r', encoding='utf-8') as sfr:
        for record in sfr:
            data += decoder(record)

    ensembles = scd.decode_packet(data)

    df = pd.DataFrame(ensembles)
    df = scd.convert_to_si(df)
    df.to_csv(out_csv)


def sfp_to_csv(input_path: Path, output_path: Path):
    """Converts Smartfin Packets to CSV format

    Args:
        input_path (Path): Input path
        output_path (Path): Output path
    """
    ensembles = []
    with open(input_path, 'rb') as handle:
        data = handle.read()
        ensembles = scd.decode_packet(data)

    df = pd.DataFrame(ensembles)
    df = scd.convert_to_si(df)
    df.to_csv(output_path)


def sf_convert(input_file: Path,
               input_type: FileFormats | None,
               output_file: Path,
               output_type: FileFormats | None,
               encoding: Encoding
               ) -> None:
    """Convert input file to output file

    Args:
        input_file (Path): Input Path
        input_type (FileFormats | None): File format, defaults to input path
        output_file (Path): Output path
        output_type (FileFormats | None): Output file format, defaults to
        output path extension
        encoding (Encoding): Record encoding

    """
    if input_type is None:
        input_type = FileFormats(input_file.suffix.lower())

    if output_type is None:
        output_type = FileFormats(output_file.suffix.lower())

    if input_type == output_type:
        shutil.copy(input_file, output_file)
        return

    decoder_map: Dict[Encoding, Callable[[str], bytes]] = {
        Encoding.BASE64: base64.b64decode,
        Encoding.BASE64URL: base64.urlsafe_b64decode,
        Encoding.BASE85: base64.b85decode
    }
    decoder = decoder_map[encoding]

    conversion_map: Dict[Tuple[FileFormats, FileFormats], ConverterType] = {
        (FileFormats.SFR, FileFormats.SFP): lambda input_path, output_path: sfr_to_sfp(input_path, output_path, decoder=decoder),
        (FileFormats.SFP, FileFormats.CSV): sfp_to_csv,
        (FileFormats.SFR, FileFormats.CSV): lambda input_path, output_path: sfr_to_csv(input_path, output_path, decoder=decoder)
    }

    conversion_type = (input_type, output_type)
    conversion_map[conversion_type](
        input_path=input_file,
        output_path=output_file
    )


def main():
    """Main entry point
    """
    configure_logging()
    parser = ArgumentParser(
        description=f'Smartfin Data Converter {__version__}'
    )
    parser.add_argument('input_file',
                        type=Path)
    parser.add_argument('--input_type',
                        default=None,
                        type=FileFormats,
                        choices=list(FileFormats))
    parser.add_argument('output_file',
                        type=Path)
    parser.add_argument('--output_type',
                        default=None,
                        type=FileFormats,
                        choices=list(FileFormats))
    parser.add_argument('-e', '--encoding',
                        type=Encoding,
                        choices=list(Encoding),
                        default=Encoding.BASE64URL)

    args = parser.parse_args()
    kwargs = vars(args)
    sf_convert(**kwargs)


if __name__ == '__main__':
    main()
