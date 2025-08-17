'''Smartfin Data Downloader
'''
import base64
import time
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List

import semantic_version
import serial
from tqdm.auto import tqdm
from smartfin_tools import __version__

def discoverAndReset(port:serial.Serial):
    port.flush()
    port.write('\r'.encode())
    port.timeout = 1
    data = port.readline()
    try:
        line = data.decode()
    except:
        pass
    if line == "Unknown command\n":
        # We are in CLI or text edit, switch back to deep sleep
        data = port.readline()
        if data.decode() == '>':
            port.write("D\r".encode())
        elif data.decode() == ':>\r\n':
            port.write('E\r'.encode())
            port.write("D\r".encode())
    elif line == 'T for MFG Test, C for C for Calibrate Mode, B for Battery State,\n':
        port.write('D\r'.encode())
    else:
        raise RuntimeError("Unknown state")

def sfDownloader():
    parser = ArgumentParser(
        description=f'Smartfin Downloader {__version__}'
    )
    parser.add_argument("port")
    parser.add_argument('--delete', '-d', action="store_true")
    parser.add_argument('--output_dir', '-o', default='./data')
    parser.add_argument('-n', '--number',
                        type=int,
                        help=('Number of files to grab, defaults to all. If '
                              'provided as N, downloads the last N files.'),
                        default=None)

    args = parser.parse_args()
    delete = args.delete

    with serial.Serial(port=args.port, baudrate=115200) as port:
        port.timeout = 1
        drop_into_cli(port)

        set_fcli(port)
        # List files
        files = get_files(port)

        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        download_data(delete, port, files, output_dir, tail=args.number)
            
        port.write('q\r'.encode())
        port.read_until('\n>'.encode())
        port.write('q\r'.encode())
        port.read_until('\n>'.encode())
        port.write('q\r'.encode())
        port.read_until('\n>'.encode())

def flogDownloader():
    parser = ArgumentParser(
        description=f'Smartfin FLOG Downloader {__version__}'
    )
    parser.add_argument('port')
    parser.add_argument('output_file', default='flog.txt')
    parser.add_argument('--clear', '-c', action='store_true')
    args = parser.parse_args()
    clear = args.clear
    output_file = args.output_file
    portname = args.port

    with serial.Serial(port=portname, baudrate=115200) as port:
        port.timeout = 1
        drop_into_cli(port)
        download_flog(clear, port, Path(output_file))
        port.write('D\r'.encode())


def download_data(delete: bool,
                  port: serial.Serial,
                  files: Dict[str, int],
                  output_dir: Path,
                  *,
                  tail: int | None = None) -> None:
    if tail is not None:
        files = {file: files[file] for file in sorted(files.keys())[-tail:]}
    for file, filesize in files.items():
        port.write('t\r'.encode())
        response = port.read_until('dump: '.encode()).decode().splitlines()
        direntry_list = {row[1].strip(): int(row[0]) for row in (
            entry.split(': ') for entry in response[1:-1])}
        direntry_idx = direntry_list[file]

        port.write(f'{direntry_idx}\r'.encode())
        header = port.read_until(f'{file}\n'.encode())
        publish_name = header.decode().splitlines()[1].split(': ')[1]

        encoded_data = ''
        n_packets = 0
        pbar = tqdm(total=filesize, unit='B', desc=publish_name,
                   unit_scale=True, unit_divisor=1024)
        while True:
            packet = port.read_until('\n'.encode()).decode()
            encoded_data += packet
            if len(packet.strip()) > 0:
                n_packets += 1
            pbar.update(len(base64.urlsafe_b64decode(packet.strip())))
            if port.in_waiting == 0:
                port.write('n'.encode())
            else:
                pbar.close()
                break


        footer = port.read_until('\n:>'.encode())

        expected_packets = int(
            footer.decode().strip().splitlines()[1].split()[0])
        if n_packets != expected_packets:
            raise RuntimeError('Packet count mismatch!')

        with open((output_dir / (publish_name + '.sfr')), 'w', encoding='utf-8') as handle:
            handle.write(encoded_data.strip())


def get_files(port: serial.Serial) -> Dict[str, int]:

    # cd into data
    port.write('c\r'.encode())
    response = port.read_until('to: '.encode()).decode().splitlines()

    dir_list = {
        entry[1].strip(): int(entry[0])
        for entry in (line.split(': ')
                      for line in response[3:-2])
    }

    dir_entry = dir_list['data']
    port.write(f'{dir_entry}\r'.encode())
    response = port.read_until('\n:>'.encode())

    # List dir
    port.write('l\r'.encode())
    response = port.read_until('\n:>'.encode()).decode().splitlines()

    files = {entry.split()[-1]: int(entry.split()[0])
             for entry in response[3:-1]}

    return files


def set_fcli(port: serial.Serial):
    # Enter debug menu
    port.write('6\r'.encode())
    port.read_until('\n>'.encode())

    # Enter File CLI
    port.write('13\r'.encode())
    port.read_until('\n:>'.encode())

def drop_into_cli(port: serial.Serial):
    port.write("#CLI".encode())
    time.sleep(0.1)
    response = port.read_all()
    if not response:
        raise RuntimeError("No response from fin!")
    data = response.decode(errors="ignore")
    lines = data.splitlines()
    fw_ver = semantic_version.Version(lines[3].split(' v')[-1])
    fw_spec = semantic_version.SimpleSpec('^3.20.0')
    if fw_ver not in fw_spec:
        port.write('q'.encode())
        raise RuntimeError(f'Invalid FW version {fw_ver}')
    if lines[-1] != '>':
        discoverAndReset(port)
        raise RuntimeError("Restart me please")

def download_flog(clear: bool, port: serial.Serial, output_path: Path):
    port.write('*\r'.encode())
    while True:
        line = port.readline().decode(errors='ignore').strip()
        if line == '*>':
            break
    port.write('11\r'.encode())
    port.readline() # Throwing away echo
    port.readline() # Throwing away title
    with open(output_path, 'w') as output:
        while True:
            line = port.readline().decode(errors='ignore')
            if line.strip() != '':
                output.write(line)
            else:
                break
    while True:
        line = port.readline().decode(errors='ignore').strip()
        if line == '*>':
            break

    if clear:
        port.write('12\r'.encode())
        while True:
            line = port.readline().decode(errors='ignore').strip()
            if line == '*>':
                break
    port.write('0\r'.encode())
    while True:
        line = port.readline().decode(errors='ignore').strip()
        if line == '>':
            break

if __name__ == "__main__":
    sfDownloader()