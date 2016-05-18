import bluetooth


class BluetoothClient(object):
    def __init__(self):
        self.address = bluetooth.read_local_bdaddr()

    def scan(self):
        print("scanning for devices")
        devices = bluetooth.discover_devices(
            flush_cache=True, lookup_class=True)

        return devices
