import serial
import time

from serial.tools import list_ports


def open_serial_port(port, baud):

    dev = None
    try:
        dev = serial.Serial(port, baud, parity="E", timeout=1)
    except Exception as e:
        print(e)
    return dev


def serial_send(dev, packet):

    dev.write(packet.encode())
    return


def serial_read(dev):
    return dev.readline().decode("utf-8")


def autodetect_jdx():

    baud = 19200
    ports_list = list_ports.comports()

    for port, desc, hwid in sorted(ports_list):
        print(f"Trying port {port}")
        try:
            dev = open_serial_port(port, baud)
            if dev is not None:
                serial_send(dev, ";000,q,q\r\n")
                data = serial_read(dev)
                print(data)
                if data != "":
                    print("Port found")
                    break
                else:
                    dev.close()
        except Exception as e:
            print(e)

    return dev


def start_stream(dev):
    serial_send(dev, ";000,s,1\r\n")
    while True:
        try:
            data = serial_read(dev)
            print(data.rstrip(), end="\r")
            time.sleep(0.01)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)

    serial_send(dev, ";000,s,0\r\n")


def main():
    dev = autodetect_jdx()
    print("Press CTRL+C to stop")
    start_stream(dev)
    dev.close()


if __name__ == "__main__":
    main()
