#!/usr/bin/env python

#   HC-06 serial blue-tooth module loop test
# This software is provided under the terms of the GNU General Public License V2.

# hc_loop_test.py
#   13-11-2019 First release V0.1


import serial
import random
import threading
import logging
from queue import Queue
import time

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

WRITE_BLOCK_SIZE = 16
READ_BLOCK_SIZE = 16


def write_thread(port, rate, ev_run):
    logging.debug('Open serial port {}, rate {} '.format(port, rate))

    ser = serial.Serial(port=port,
                        baudrate=rate,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        xonxoff=False,
                        rtscts=False,
                        dsrdtr=False,
                        timeout=None,
                        write_timeout=None)

    logging.debug('Init random data block size {} '.format(WRITE_BLOCK_SIZE))
    init = [random.randrange(0, 256) for _ in range(0, WRITE_BLOCK_SIZE)]
    data = bytes(init)

    logging.debug('Waiting for start event ...')
    ev_run.wait()

    logging.debug('Running ...')
    ct = 0
    t0 = time.time()
    while ev_run.is_set():
        ct += ser.write(data)
        t1 = time.time()
        dt = t1 - t0
        if dt > 1:
            t0 = t1
            mr = ct / dt
            ct = 0
            logging.debug('Writing rate {:.0f} byte/s'.format(mr))

    ser.close()
    logging.debug('Exit')


def read_thread(port, rate, ev_run):
    logging.debug('Open serial port {}, rate {} '.format(port, rate))

    ser = serial.Serial(port=port,
                        baudrate=rate,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        xonxoff=False,
                        rtscts=False,
                        dsrdtr=False,
                        timeout=None,
                        write_timeout=None)

    logging.debug('Waiting for start event ...')
    ev_run.wait()

    logging.debug('Running ...')
    ct = 0
    t0 = time.time()
    while ev_run.is_set():
        ct += len(ser.read(READ_BLOCK_SIZE))
        t1 = time.time()
        dt = t1 - t0
        if dt > 1:
            t0 = t1
            mr = ct / dt
            ct = 0
            logging.debug('Read rate {:.0f} byte/s'.format(mr))

    ser.close()
    logging.debug('Exit')


ev_run = threading.Event()

wt = threading.Thread(target=write_thread, name='WriteThread',
                      args=('COM11', 9600, ev_run))

rt = threading.Thread(target=read_thread, name='ReadThread',
                      args=('COM8', 9600, ev_run))

wt.start()
rt.start()

time.sleep(5)

ev_run.set()

time.sleep(10)

ev_run.clear()

wt.join()
rt.join()

