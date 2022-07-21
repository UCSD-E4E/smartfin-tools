import serial

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
            continue;
        elif data.decode(errors='ignore') == '>':
            break
            
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