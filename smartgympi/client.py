import argparse
import configparser
import logging
import logging.config
import sys
import threading

import redis
import requests

from smartgympi.bluetooth import BluetoothClient

log = logging.getLogger()

redis_client = None

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
        self.expiration_time = int(config['redis']['expiration_time'])
        self.max_threads = int(config['app:main']['max_threads'])

    def main(self):
        try:
            while True:
                devices = self.bluetooth_client.scan()
                for device in devices:
                    if threading.active_count() == self.max_threads:
                        log.critical("Number of maximum threads reached")
                        log.critical("Waiting for threads to become available")
                        continue

                    log.info("Device found: {}".format(device))
                    if redis_client.get(device[0]):
                        # The device is foudn in the cache which means it
                        # was persisted very recently. We should not try
                        # persisting it again untill it's expired.
                        log.info('device found in cache, continuing..')
                        continue

                    log.info("Persisting..")
                    persist_thread = threading.Thread(
                        target=self._persist,
                        args=(device[0], device[1], device[2]))
                    persist_thread.daemon = True
                    persist_thread.start()
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
        request = requests.post(self.remote_url, json=body)

        if request.status_code == 200:
            log.info("Success")
            log.info(request.text)
            redis_client.setex(address,
                               self.expiration_time,
                               name)
        else:
            log.critical("Something went wrong..")
            log.critical("Status code: {}".format(request.status_code))
            log.critical(request.text)


if __name__ == "__main__":
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    logging.config.fileConfig(config)

    redis_client = redis.StrictRedis(host=config['redis']['host'],
                                     port=config['redis']['port'],
                                     db=config['redis']['db'])

    client = Client()
    client.main()
