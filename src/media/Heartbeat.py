from Communication import Communication
import json
import time

class Heartbeat(Communication):
    device_id = 0
    def __init__(self, device):
        self.device = device
        self.timestamp = time.ctime(time.time())
        self.device_id = self.device.id
        self.playStatus = self.device.playStatus()
    def heartbeat(self):
        return(json.dumps(
                {
                    'type': 'heartbeat',
                    'device-id': self.device_id,
                    'timestamp': self.timestamp,
                    'device-type': self.device.deviceType,
                    'playStatus': self.playStatus,
                }
            )
        )
    @staticmethod
    def heartbeatString(device_id:int = 0, timestamp:str = time.ctime(time.time()), deviceType:str = 'client', playStatus:str = "Not Playing"):
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

#if __name__ == "__main__":
