import bluetooth


class BluetoothClient(object):
    def __init__(self, config):
        # Read the device's MAC address and removes any line breaks
        self.device_address = config['app:main']['local_MAC_address']

    def scan(self):
        print("scanning for devices")
        devices = bluetooth.discover_devices(
            flush_cache=True, lookup_class=True)

        return devices
