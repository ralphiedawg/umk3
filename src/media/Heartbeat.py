from Controller import Controller
import json
import time

class Heartbeat:
    device_id = 0
    def __init__(self, device:Controller = Controller()):
        self.device = device
        self.timestamp = time.ctime(time.time())
        self.device_id = self.device.id
    def heartbeat(self):
        return(json.dumps(
                {
                    "device-id": self.device_id,
                    "timestamp": self.timestamp,
                    "device-type": self.device.deviceType
                }
            )
        )
    @staticmethod
    def heartbeatString(device_id:int = 0, timestamp:str = time.ctime(time.time()), deviceType:str = 'client'):
        return(json.dumps(
                {
                    "device-id": device_id,
                    "timestamp": timestamp,
                    "device-type": deviceType
                }
            )
        )


if __name__ == "__main__":
    ct1 = Controller()
    ct2 = Controller()
    ct3 = Controller()
    print(Heartbeat(ct1).heartbeat())
    print(Heartbeat(ct2).heartbeat())
    print(Heartbeat(ct3).heartbeat())
