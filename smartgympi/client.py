import argparse
import base64
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
        self.auth_header = self.get_auth_header()

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
        redis_client.setex(address,
                           self.expiration_time,
                           name)

        body = {
            "name": name,
            "device_address": address,
            "device_class": device_class,
            "client_address": self.bluetooth_client.local_address
        }
        request = requests.post(self.remote_url, json=body,
                                headers=self.auth_header)

        log.info("Status code: {}".format(request.status_code))
        if request.status_code == 200:
            log.info("Success")
            log.info(request.text)
        elif request.status_code == 403:
            # This is due to the access token expiring.
            # So we request a new token and retry the request
            log.info("Access token expired")
            self.auth_header = self.get_auth_header()
            self._persist(address, name, device_class)
        elif request.status_code == 404:
            log.info("Device not found")
        else:
            log.critical("Something went wrong..")
            log.critical(request.text)

    def get_auth_header(self):
        try:
            client_id = config['oauth']['client_id']
            client_secret = config['oauth']['client_secret']
            token_url = config['oauth']['access_token_url']
        except KeyError:
            log.critical("OAuth settings not correctly specified",
                         exc_info=True)
            sys.exit()

        client_credentials = '{}:{}'.format(
            client_id, client_secret)

        # b64 encode expects bytes. After that we convert from bytes to string
        encoded_client_credentials = base64.b64encode(
            client_credentials.encode('utf-8')).decode('utf-8')
        client_auth_header = {
            'Authorization': 'Basic {}'.format(encoded_client_credentials)
        }
        request_body = {'grant_type': 'client_credentials'}

        access_token_request = requests.post(token_url,
                                             json=request_body,
                                             headers=client_auth_header)

        if access_token_request.status_code != 200:
            # Without the access code we can't persist any devices
            log.critical("Can't get access token")
            log.critical(access_token_request.status_code)
            sys.exit()

        response_body = access_token_request.json()

        auth_header = {
            'Authorization': '{} {}'.format(
                response_body['token_type'],
                response_body['access_token'])
        }

        return auth_header

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
