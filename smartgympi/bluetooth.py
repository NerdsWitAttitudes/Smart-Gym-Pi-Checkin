import bluetooth
import logging

log = logging.getLogger()


class BluetoothClient(object):

    def __init__(self, config):
        self.local_address = config['app:main']['local_MAC_address']

    def scan(self):
        log.info("scanning for devices")
        return bluetooth.discover_devices(
            lookup_names=True,
            flush_cache=True,
            lookup_class=True)
