'''SF Verify
'''
import argparse
import binascii
import sys
from pathlib import Path

from smartfin_tools import __version__


def compute_crc32(path: Path):
    """Computes the CRC32 of the SFP file

    Args:
        path (Path): Path to file
    """
    with open(path, 'rb') as handle:
        data = handle.read()
    crc = binascii.crc32(data, 0) & 0xFFFFFFFF
    print(f'CRC32: {crc:08X}')


def main():
    """Main entry point
    """
    parser = argparse.ArgumentParser(
        description=f'Smartfin Data Verifier {__version__}'
    )
    parser.add_argument('input_file', type=Path)

    args = parser.parse_args()
    input_path: Path = args.input_file

    if input_path.suffix.lower() != '.sfp':
        print('Needs to be a .sfp file!')
        sys.exit(1)

    compute_crc32(input_path)


if __name__ == '__main__':
    main()
