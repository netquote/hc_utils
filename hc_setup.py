#!/usr/bin/env python

#   HC-06 serial blue-tooth module setup tool
# This software is provided under the terms of the GNU General Public License V2.

# hc_setup.py
#   13-11-2019 First release V0.1

import argparse
import serial
import time
import logging

# List of available rates for HC-06
RATE_LIST = {b'1': b'1200',
             b'2': b'2400',
             b'3': b'4800',
             b'4': b'9600',
             b'5': b'19200',
             b'6': b'38400',
             b'7': b'57600',
             b'8': b'115200',
             b'9': b'230400',
             b'A': b'460800',
             b'B': b'921600',
             b'C': b'1382400'}


def open_port(port, rate, parity=serial.PARITY_NONE):
    """ Open serial port """
    return serial.Serial(port=port,
                         baudrate=rate,
                         bytesize=serial.EIGHTBITS,
                         parity=parity,
                         stopbits=serial.STOPBITS_ONE,
                         xonxoff=False,
                         rtscts=False,
                         dsrdtr=False,
                         timeout=1,
                         write_timeout=1)


def send_cmd(ser, cmd):
    """ Send AT command and wait for 'OK'
Returns None for errors or binary data """
    # Write to serial port
    logging.debug('{}'.format(cmd))
    ser.write(cmd)
    # Wait for replay
    res = ser.read(30)
    logging.debug('{}'.format(res))

    # Check for OK and return result if any
    if len(res) >= 2 and res[0:2] == b'OK':
        return res[2:]

    elif len(res) > 0:
        print("Unknown replay: {} ".format(res))
        return res

    return None


def open_scan(port, rate_hint, parity_hint):
    """ Try to detect AT device baudrate """
    print("Guessing bit-rate and parity on {} ...".format(port))
    for bitrate in rate_hint:
        for parity in parity_hint:
            # Setup and open serial port
            print("  Rate: {}, parity: {} ".format(bitrate, parity))
            ser = open_port(port=port, rate=bitrate, parity=parity)
            res = send_cmd(ser, b'AT')
            if res == b'':
                return ser
            ser.close()
            # Sleeps for 100 ms before reopen
            time.sleep(0.1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('device_port', type=str,
                        help="Serial configuration device port name 'COM3' for Windows and '/dev/ttyUSB0' for Linux ")
    parser.add_argument('-r', '--rate', type=str, default='',
                        help="Serial port configuration bit-rate, empty for auto-scan")
    parser.add_argument('-p', '--parity', type=str, default='',
                        choices=['N', 'O', 'E'],
                        help="Serial port configuration parity, empty for auto-scan")
    parser.add_argument('--set-rate', type=str, default='',
                        help="Set new data bit-rate [1 .. C] or [1200 .. 1382400]")
    parser.add_argument('--set-pin', type=str, default='',
                        help="Set pairing PIN code")
    parser.add_argument('--set-name', type=str, default='',
                        help="Set device name")
    parser.add_argument('--set-parity', type=str, default='',
                        choices=['N', 'O', 'E'],
                        help="Set parity bit [N = None, O = Odd, E = Even]")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Set verbosity on")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(message)s')

    scan_rate = True
    default_rate = 9600
    if len(args.rate) > 0:
        for k, v in RATE_LIST.items():
            if args.rate.encode() == k or args.rate.encode() == v:
                default_rate = int(v)
                scan_rate = False
                break

    scan_parity = True
    default_parity = serial.PARITY_NONE
    if len(args.parity) > 0:
        if args.parity == 'O':
            default_parity = serial.PARITY_ODD
            scan_parity = False
        elif args.parity == 'E':
            default_parity = serial.PARITY_EVEN
            scan_parity = False

    if scan_rate or scan_parity:

        if scan_rate:
            rl = [int(v) for v in RATE_LIST.values()]
        else:
            rl = [default_rate]

        if scan_parity:
            pl = [serial.PARITY_NONE, serial.PARITY_ODD, serial.PARITY_EVEN]
        else:
            pl = [default_parity]

        ser = open_scan(args.device_port, rl, pl)
        if ser is not None:
            default_rate = ser.baudrate
            default_parity = ser.parity
            print("AT device detected.")
            ser.close()

    print("Open serial port: {}, bit-rate: {}, parity: {} ".format(args.device_port, default_rate, default_parity))
    ser = open_port(args.device_port, default_rate, default_parity)
    res = send_cmd(ser, b'AT+VERSION')
    print("Device version: {} ".format(res.decode('utf8')))

    if res == b'linvorV1.5' or res == b'linvorV1.8':

        if len(args.set_name) > 0:
            res = send_cmd(ser, b'AT+NAME'+args.set_name.encode())
            if res == b'setname':
                print("Set name OK")
            elif res is not None:
                print("Set name {} ".format(res.decode('utf8')))

        if len(args.set_pin) > 0:
            res = send_cmd(ser, b'AT+PIN'+args.set_pin.encode())
            if res == b'setPIN':
                print("Set pin OK")
            elif res is not None:\
                print("Set pin {} ".format(res.decode('utf8')))

        if len(args.set_rate) > 0:
            for k, v in RATE_LIST.items():
                if (k == args.set_rate.encode()) or (v == args.set_rate.encode()):
                    res = send_cmd(ser, b'AT+BAUD'+k)
                    if res is not None:
                        print("Set baud {} ".format(res.decode('utf8')))
                    break

        if len(args.set_parity) > 0:
            res = send_cmd(ser, b'AT+P'+args.set_parity.encode())
            if res is not None:
                print("Set parity {} ".format(res.decode('utf8')))

    ser.close()
