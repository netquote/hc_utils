HC-06 serial bluetooth setup tool

usage: hc_setup.py [-h] [-r RATE] [-p {N,O,E}] [--set-rate SET_RATE]
                   [--set-pin SET_PIN] [--set-name SET_NAME]
                   [--set-parity {N,O,E}] [-v]
                   device_port

positional arguments:
  device_port           Serial configuration device port name 'COM3' for
                        Windows and '/dev/ttyUSB0' for Linux

optional arguments:
  -h, --help            show this help message and exit
  -r RATE, --rate RATE  Serial port configuration bit-rate, empty for auto-
                        scan
  -p {N,O,E}, --parity {N,O,E}
                        Serial port configuration parity, empty for auto-scan
  --set-rate SET_RATE   Set new data bit-rate [1 .. C] or [1200 .. 1382400]
  --set-pin SET_PIN     Set pairing PIN code
  --set-name SET_NAME   Set device name
  --set-parity {N,O,E}  Set parity bit [N = None, O = Odd, E = Even]
  -v, --verbose         Set verbosity on

This script automatically tries to detect device serial communication bit-rate and parity. 
If you provide hints about parity or bit-rate with '-p' and '-r' options, detection will be faster.

Linux platforms:
  $ ./hc_setup.py /dev/ttyUSB0 --set-rate 115200 --set-pin 1234 --set-name BTS00 --set-parity N

Windows platforms:
  $ python hc_setup.py COM1 --set-rate 115200 --set-pin 1234 --set-name BTS00 --set-parity N
