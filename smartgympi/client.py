import argparse
import configparser
import logging
import logging.config
import sys

import requests

from smartgympi.scan import BluetoothClient

log = logging.getLogger()

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
        self.bluetooth_client = BluetoothClient(config)
        self.remote_url = config['app:main']['remote_url']

    def main(self):
        try:
            devices = self.bluetooth_client.scan()
            for device in devices:
                log.info("Device found: {}".format(device))
                log.info("Persisting..")
                self._persist(
                    address=device[0],
                    name=device[1],
                    device_class=device[2]
                )
        except OSError:
            log.critical("No bluetooth interface found. Terminating...")
            sys.exit()

    def _persist(self, address, name, device_class):
        body = {
            "name": name,
            "device_address": address,
            "device_class": device_class,
            "client_address": self.bluetooth_client.local_address
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
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    logging.config.fileConfig(config)

    client = Client()
    client.main()
