import json
import time

class Heartbeat():
    device_id = 0
    def __init__(self, device):
        self.device = device
        self.device_id = self.device.id
        self.playStatus = self.device.playStatus()
    def heartbeat(self):
        return(json.dumps(
                {
                    'type': 'heartbeat',
                    'device-id': self.device_id,
                    'timestamp': str(time.time()),
                    'device-type': self.device.deviceType,
                    'playStatus': self.playStatus,
                }
            )
        )
    @staticmethod
    def heartbeatString(device_id:int = 0, timestamp:str = str(time.time()), deviceType:str = 'client', playStatus:str = "not_playing "):
        return(json.dumps(
                {
                    'type': 'heartbeat',
                    'device-id': device_id,
                    'timestamp': timestamp,
                    'device-type': deviceType,
                    'playStatus': playStatus
                }
            )
        )

"""
if __name__ == "__main__":
    c1 = Client()
    h1 = Heartbeat(c1)
    print(h1.heartbeat())
"""
