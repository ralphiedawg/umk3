import json

class RecencyArbiter:
    def __init__(self, heartbeats=None):
        self.heartbeats = {}
        if heartbeats:
            self.heartbeats = self._enumerate_givens(heartbeats)
    """
    {"type": "heartbeat", "device-id": 1, "timestamp": "1777998089.264807", "device-type": "client", "play-status": "not_playing"}
    {"type": "heartbeat", "device-id": 1, "timestamp": "1777998099.360051", "device-type": "client", "play-status": "playing"}
    """
    def _pull_id(self, heartbeat) -> int:
        data = json.loads(heartbeat)
        return data['device-id']
    def _enumerate_givens(self, heartbeats: list) -> dict:
        final = {}
        for heartbeat in heartbeats:
            device_id = self._pull_id(heartbeat)
            final[device_id] = heartbeat
        return final
    def arbitrate(self, raw_heartbeat) -> int:
        """Check heartbeat against stored list of old heartbeats, returns value of changed client, 0 if not"""
        new = json.loads(raw_heartbeat)
        device_id = self._pull_id(raw_heartbeat)

        raw_old = self.heartbeats[device_id]
        if device_id  not in self.heartbeats:
            self.heartbeats[device_id] = raw_heartbeat
            return device_id
        old = json.loads(raw_old)

        if (
            (old['play-status'] != new['play-status']) 
            and (float(old['timestamp']) < float(new['timestamp']))
        ):
            self.heartbeats[device_id] = raw_heartbeat

            return device_id
        return 0

if __name__ == '__main__':
    beats = [
        '{"type": "heartbeat", "device-id": 3, "timestamp": "1777998089.264807", "device-type": "client", "play-status": "not_playing"}',
        '{"type": "heartbeat", "device-id": 5, "timestamp": "1777998089.264807", "device-type": "client", "play-status": "not_playing"}',
        '{"type": "heartbeat", "device-id": 1, "timestamp": "1777998099.360051", "device-type": "client", "play-status": "playing"}'
    ]
    c = RecencyArbiter(beats)
