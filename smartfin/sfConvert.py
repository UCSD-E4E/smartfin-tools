from argparse import ArgumentParser
from base64 import b85decode
from pathlib import Path
import shutil

import pandas as pd

import decoder as scd


def sfrToSfp(in_sfr: Path, out_sfp: Path, no_strip_padding: bool=False):
    with open(in_sfr, 'r') as sfr:
        with open(out_sfp, 'wb') as sfp:
            for record in sfr:
                packet = b85decode(record.strip())
                if not no_strip_padding:
                    packet = scd.stripPadding(packet)
                sfp.write(packet)

def sfrToCsv(in_sfr: Path, out_csv: Path):
    ensembles = []
    with open(in_sfr, 'r') as sfr:
        for record in sfr:
            ensembles.extend(scd.decodeRecord(record.strip()))
    
    df = pd.DataFrame(ensembles)
    df = scd.convertToSI(df)
    df.to_csv(out_csv, index=False)

def sfpToCsv(in_sfp: Path, out_csv: Path):
    ensembles = []
    with open(in_sfp, 'rb') as sfp:
        data = sfp.read()
        ensembles = scd.decodePacket(data)
    
    df = pd.DataFrame(ensembles)
    df = scd.convertToSI(df)
    df.to_csv(out_csv, index=False)

def main():
    parser = ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--input_type', default=None, nargs=1, choices=['sfr', 'sfp'])
    parser.add_argument('output')
    parser.add_argument('--output_type', default=None, nargs=1, choices=['sfp', 'csv'])
    parser.add_argument('--no_strip_padding', action='store_true')

    args = parser.parse_args()
    input_file = Path(args.input)
    if not input_file.is_file():
        raise RuntimeError("Not a file!")
    
    if args.input_type == None:
        if input_file.suffix.lower() == '.sfr':
            input_type = 'sfr'
        elif input_file.suffix.lower() == '.sfp':
            input_type = 'sfp'
        else:
            raise RuntimeError("Ambiguous input type!")
    else:
        input_type = args.input_type

    output_file = Path(args.output)
    if args.output_type == None:
        if output_file.suffix.lower() == '.sfp':
            output_type = 'sfp'
        elif output_file.suffix.lower() == '.csv':
            output_type = 'csv'
        else:
            raise RuntimeError("Ambiguous output type!")
    else:
        output_type = args.output_type

    if input_type == output_type:
        shutil.copy(input_file, output_file)
    
    if input_type == 'sfr' and output_type == 'sfp':
        sfrToSfp(input_file, output_file, no_strip_padding=args.no_strip_padding)
    elif input_type == 'sfp' and output_type == 'csv':
        sfpToCsv(input_file, output_file)
    elif input_type == 'sfr' and output_type == 'csv':
        sfrToCsv(input_file, output_file)
    else:
        raise RuntimeError("Unknown conversion")

if __name__ == '__main__':
    main()