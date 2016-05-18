# file: inquiry.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: performs a simple device inquiry followed by a remote name request of
#       each discovered device
# $Id: inquiry.py 401 2006-05-05 19:07:48Z albert $
#

import bluetooth


class BluetoothScanner(object):
    def scan():
        print("scanning for devices")
        devices = bluetooth.discover_devices(
            flush_cache=True, lookup_class=True)

        return devices
