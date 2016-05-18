import requests

from smartgympi.scan import BluetoothClient


class Client(object):
    def __init__(self):
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
            print("Success")
            print(request.text)
        else:
            print("Something went wrong..")
            print("Status code: {}".format(request.status_code))
            print(request.text)


if __name__ == "__main__":
    client = Client()
    client.main()
