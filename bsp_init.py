#!/usr/bin/python3

import os
from itertools import chain
import subprocess


def new_device(driver, addr, bus, devdir):
    if not os.path.exists(os.path.join(bus, devdir)):
        try:
            with open("%s/new_device" % bus, "w") as f:
                f.write("%s 0x%x\n" % (driver, addr))
        except Exception as e:
            print("Unexpected error initialize device %s:0x%x:%s: %s" % (driver, addr, bus, e))
    else:
        print("Device %s:%x:%s already exists." % (driver, addr, bus))

def new_devices(new_device_list):
    for (driver, addr, bus, devdir) in new_device_list:
        new_device(driver, addr, bus, devdir)

def new_i2c_device(driver, addr, bus_number):
    bus = '/sys/bus/i2c/devices/i2c-%d' % bus_number
    devdir = "%d-%4.4x" % (bus_number, addr)
    return new_device(driver, addr, bus, devdir)

def new_i2c_devices(new_device_list):
    for (driver, addr, bus_number) in new_device_list:
        new_i2c_device(driver, addr, bus_number)

def insmod(module: str) -> bool:
    subprocess.check_call(f"insmod {module}")
    return True

def baseconfig():
    insmod('optoe')
    for m in [ 'cpld', 'fan', 'psu', 'leds', 'thermal', 'sys' ]:
        insmod("x86-64-accton-as7926-40xfb-%s.ko" % m)

    ########### initialize I2C bus 0 ###########
    new_i2c_devices([
            # initialize multiplexer (PCA9548)
            ('pca9548', 0x77, 0), # i2c 1-8

            # initiate  multiplexer (PCA9548) of bottom board
            ('pca9548', 0x76, 1), # i2c 9-16
            ('pca9548', 0x70, 1), # i2c 17-24
            ('pca9548', 0x73, 9), # i2c 25-32

            # initiate multiplexer for QSFP ports
            ('pca9548', 0x74, 25), # i2c 33-40
            ('pca9548', 0x74, 26), # i2c 41-48
            ('pca9548', 0x74, 27), # i2c 49-56
            ('pca9548', 0x74, 28), # i2c 57-64
            ('pca9548', 0x74, 29), # i2c 65-72

            # initiate multiplexer for FAB ports
            ('pca9548', 0x74, 17), # i2c 73-80
            ('pca9548', 0x74, 18), # i2c 81-88

            #initiate CPLD
            ('as7926_40xfb_cpld2', 0x62, 12),
            ('as7926_40xfb_cpld3', 0x63, 13),
            ('as7926_40xfb_cpld4', 0x64, 20)
            ])

    for port in chain(range(1, 11), range(21, 31)):
        subprocess.call('echo 0 > /sys/bus/i2c/devices/12-0062/module_reset_%d' % port, shell=True)

    for port in chain(range(11, 21), range(31, 41)):
        subprocess.call('echo 0 > /sys/bus/i2c/devices/13-0063/module_reset_%d' % port, shell=True)

    for port in range(41, 54):
        subprocess.call('echo 0 > /sys/bus/i2c/devices/20-0064/module_reset_%d' % port, shell=True)

    # initialize QSFP port(0-39), FAB port(40-52)
    port_i2c_bus = [33, 34, 37, 38, 41, 42, 45, 46, 49, 50,
                    53, 54, 57, 58, 61, 62, 65, 66, 69, 70,
                    35, 36, 39, 40, 43, 44, 47, 48, 51, 52,
                    55, 56, 59, 60, 63, 64, 67, 68, 71, 72,
                    85, 76, 75, 74, 73, 78, 77, 80, 79, 82,
                    81, 84, 83]

    for port in range(0, 53):
        new_i2c_device('optoe1', 0x50, port_i2c_bus[port])
        subprocess.call('echo port%d > /sys/bus/i2c/devices/%d-0050/port_name' % (port, port_i2c_bus[port]), shell=True)

    # initialize SFP port 53-54
    new_i2c_device('optoe2', 0x50, 30)
    subprocess.call('echo port53 > /sys/bus/i2c/devices/30-0050/port_name', shell=True)
    new_i2c_device('optoe2', 0x50, 31)
    subprocess.call('echo port54 > /sys/bus/i2c/devices/31-0050/port_name', shell=True)

    return True

baseconfig()