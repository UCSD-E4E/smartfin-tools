from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Optional
import serial

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

def main():
    parser = ArgumentParser()
    parser.add_argument("port")
    parser.add_argument('--delete', '-d', action="store_true")
    parser.add_argument('--output_dir', '-o', default='.')

    args = parser.parse_args()
    delete = args.delete

    with serial.Serial(port=args.port, baudrate=115200) as port:
        port.timeout = 1
        drop_into_cli(port)
        
        # List files
        files = get_files(port)
        print(files)

        Path(args.output_dir).mkdir(parents=True, exist_ok=True)

        base85data = download_data(delete, port, files)
            
        port.write('D\r'.encode())

        for file, data in base85data.items():
            output_path = Path(args.output_dir, file)
            output_path = output_path.with_suffix('.sfr').as_posix()
            print(output_path)
            with open(output_path, 'w') as f:
                for line in data:
                    f.write(line)
                    f.write('\n')
        print(f'Downloaded {len(base85data)} files')

def download_data(delete: bool, port: serial.Serial, files: List[str]) -> Dict[str, List[str]]:
    # Download files
    port.write('R\r'.encode())
    filename: Optional[str] = None
    base85data: Dict[str, List[str]] = {}
    format = ''
    while True:
        while True:
            data = port.readline().decode(errors='ignore')
            if data == 'R\r\n':
                continue
            elif data == 'N\r\n':
                continue
            elif data == 'End of Directory\n':
                break
            elif data.strip() == 'Press N to go to next file, C to copy, R to read it out (base85), U to read it out (uint8_t), D to delete, E to exit':
                format == 'base85'
                continue
            elif data.strip() == 'Press N to go to next file, C to copy, R to read it out (base64), U to read it out (uint8_t), D to delete, E to exit':
                format == 'base64'
                continue
            elif data.strip() == 'Press N to go to next file, C to copy, R to read it out (base64url), U to read it out (uint8_t), D to delete, E to exit':
                format == 'base64url'
                continue
            elif data == '':
                continue
            elif data.strip().split()[0] in files:
                filename = data.split()[0]
                continue
            elif data == ':>':
                break
            else:
                discoverAndReset(port)
                raise RuntimeError("Unknown state")
        if data == 'End of Directory\n':
            break

        port.write('R\r'.encode())
        while True:
            data = port.readline().decode(errors='ignore')
            if data == 'R\r\n':
                continue
            elif data == 'N\r\n':
                continue
            elif data.startswith('Publish Header'):
                output_filename = data.split()[-1]
                continue
            elif data.strip() == '':
                continue
            elif data.strip().endswith('chars of base85 data'):
                continue
            elif data.strip().endswith('packets'):
                continue
            elif data == ':>':
                if delete == True:
                    port.write('D\r'.encode())
                    while True:
                        data = port.readline().decode()
                        if data == ':>':
                            break
                port.write('N\r'.encode())
                break
            else:
                    # this is file data
                if output_filename in base85data:
                    base85data[output_filename].append(data.strip())
                else:
                    base85data[output_filename] = [data.strip()]
    port.write('E\r'.encode())
    return base85data

def get_files(port: serial.Serial):
    files: List[str] = []
    port.write('L\r'.encode())
    while True:
        data = port.readline().decode(errors='ignore')
        if data == '>':
            break
        elif data == 'L\r\n':
            continue
        files.append(data.split()[0])
    return files

def drop_into_cli(port: serial.Serial):
    port.write("#CLI\r".encode())
    data = port.readline()
    if data.decode(errors="ignore") != "Next State: STATE_CLI\n":
        discoverAndReset(port)
        raise RuntimeError("Restart me please")
        
        # Wait for '>'
    while True:
        data = port.readline()
        if data.decode(errors='ignore') == '':
            raise RuntimeError("Unexpected no data!")
        elif data.decode(errors='ignore') == '>':
            break

if __name__ == "__main__":
    main()