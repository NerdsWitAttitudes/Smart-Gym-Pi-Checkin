import argparse
import configparser
import logging

import requests

from smartgympi.scan import BluetoothClient

config = None
log = None

parser = argparse.ArgumentParser(
    description="""
        Scans area for bluetooth devices and checks them in and out of the
        Smart Gym API
    """
)

parser.add_argument(
    '--config', default='settings.ini', type=str,
    help="Argument that takes a configuration file"
)


class Client(object):
    def __init__(self):
        args = parser.parse_args()
        config_parser = configparser.ConfigParser()

        global config
        config = config_parser.read(args.config)

        global log
        log = logging.getLogger(__name__)

        self.bluetooth_client = BluetoothClient()
        self.remote_url = ''

    def main(self):
        address, device_class = self.bluetooth_client.scan()
        self._persist(address, device_class)

    def _persist(self, address, device_class):
        body = {
            "device_address": address,
            "device_class": device_class,
            "client_address": self.bluetooth_client.address
        }
        request = requests.post(self.remote_url, data=body)

        if request.status_code == 200:
            log.info("Success")
            log.info(request.text)
        else:
            log.critical("Something went wrong..")
            log.critical("Status code: {}".format(request.status_code))
            log.critical(request.text)


if __name__ == "__main__":
    client = Client()
    client.main()