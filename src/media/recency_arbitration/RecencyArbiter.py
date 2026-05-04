import json

from src.media.recency_arbitration.MacOSWrapper import MacOSWrapper

"""{"type": "heartbeat", "device-id": 1, "timestamp": "1777911430.6075552", "device-type": "client", "play-status": "not_playing"}"""
class RecencyArbiter():
    def __init__(self, heartbeats):
        self.heartbeats = heartbeats
        self.old_beats = [] # Last recieved heartbeat for every client
    async def determine_active(self) -> int:
        changed = []
        for heartbeat in self.heartbeats:
            heartbeat = json.loads(heartbeat)
            id = heartbeat['device-id']
            current = heartbeat['play-status']
            old = [item for item in self.old_beats if item['device-id'] == id]
        return 1
