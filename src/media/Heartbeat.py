from Client import Client
import json
import time

class Heartbeat:
    device_id = 0
    def __init__(self, device:Client = Client()):
        self.device = device
        self.timestamp = time.ctime(time.time())
        self.device_id = self.device.id
        self.playStatus = "Not Playing"
    def heartbeat(self):
        return(json.dumps(
                {
                    "device-id": self.device_id,
                    "timestamp": self.timestamp,
                    "device-type": self.device.deviceType,
                    "playStatus": self.playStatus,
                }
            )
        )
    @staticmethod
    def heartbeatString(device_id:int = 0, timestamp:str = time.ctime(time.time()), deviceType:str = 'client', playStatus:str = "Not Playing"):
        return(json.dumps(
                {
                    "device-id": device_id,
                    "timestamp": timestamp,
                    "device-type": deviceType,
                    "playStatus": playStatus
                }
            )
        )

if __name__ == "__main__":
    ct1 = Client()
    ct2 = Client()
    ct3 = Client()
    print(Heartbeat(ct1).heartbeat())
    print(Heartbeat(ct2).heartbeat())
    print(Heartbeat(ct3).heartbeat())
