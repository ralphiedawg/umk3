# Distance Gesture Implementation Plan

## Overview
Implement a reusable distance-based gesture system that allows complex multi-gesture sequences. Primary use case: Shaka activation → Peace sign → Volume control via finger distance.

---

## Phase 1: Gesture Configuration (NEW)

### 1.1 Create `src/gesture/gesture_config.json`
Move hardcoded gesture data out of `Landmarker.py` into a centralized config file.

**Structure:**
```json
{
  "poses": {
    "open_palm": [true, true, true, true, true],
    "peace": [false, true, true, false, false],
    "shaka": [true, false, false, false, true],
    "closed_fist": [false, false, false, false, false],
    "i": [false, false, false, false, true],
    "point": [false, true, false, false, false],
    "spiderman": [false, true, false, false, true],
    "justin": [false, false, true, false, false],
    "rock_on": [true, true, false, false, true]
  },
  "commands": {
    "open_palm": "pause",
    "i": "back5",
    "point": "skip5",
    "shaka": "listen"
  },
  "distance_gestures": {
    "peace": {
      "window_duration": 2,
      "stabilization_wait": 0.5,
      "command_type": "volume",
      "finger_indices": [8, 4],
      "distance_range": [0.05, 0.3],
      "steps": 20,
      "min_distance": 0.05,
      "max_distance": 0.3
    }
  }
}
```

**Purpose:**
- Centralize gesture definitions
- Enable easy addition of new distance gestures (e.g., rock_on for zoom, justin for speed)
- Decouple gesture logic from Landmarker code

---

## Phase 2: GestureSequence Class (REFACTOR)

### 2.1 Update `src/gesture/GestureSequence.py`
Extend to track distance gesture states.

**New methods:**
```python
class GestureSequence:
    def __init__(self, activation_gesture: str, window_dur: int, commands_allowed: int):
        self.activation_gesture = activation_gesture
        self.window_duration = window_dur
        self.commands_allowed = commands_allowed
        
        self.active = False
        self.activation_time = 0
        self.commands_sent = 0
    
    def activate(self):
        """Activate sequence, record timestamp"""
        self.active = True
        self.activation_time = time.time()
        self.commands_sent = 0
    
    def is_active(self) -> bool:
        """Check if window is still open"""
        if not self.active:
            return False
        elapsed = time.time() - self.activation_time
        return elapsed < self.window_duration
    
    def can_send_command(self) -> bool:
        """Check if active and command quota not exceeded"""
        return self.is_active() and self.commands_sent < self.commands_allowed
    
    def record_command(self):
        """Increment command count"""
        self.commands_sent += 1
    
    def deactivate(self):
        """End sequence"""
        self.active = False
```

---

## Phase 3: Distance Gesture State Machine (NEW)

### 3.1 Create `src/gesture/DistanceGestureTracker.py`
Track state progression through distance gestures.

**States:**
1. `IDLE` - Waiting for activation gesture (shaka)
2. `WAITING_FOR_TRIGGER` - Shaka detected, waiting for distance gesture trigger (peace)
3. `STABILIZING` - Trigger gesture detected, waiting 0.5s for hand to stabilize
4. `TRACKING` - Distance tracking active (2 seconds)
5. `COMPLETE` - Gesture sequence complete, waiting for next shaka

**Responsibilities:**
- Manage state transitions
- Track timing for stabilization wait (0.5s after peace detected)
- Track timing for distance window (2 seconds)
- Calculate volume steps based on distance changes
- Determine when to send volume update commands (every 5% threshold)

**Key method:**
```python
def process_frame(pose, hand_landmarks, current_time):
    """
    Process current frame and determine if action needed
    Returns: None or command_dict with 'type' and 'data'
    """
    # State machine logic
    # Returns volume command when threshold crossed
```

---

## Phase 4: Distance Gesture Logic (NEW)

### 4.1 Update `src/gesture/GestureUtils.py`
Add distance-to-command mapping.

**New methods:**
```python
class GestureUtils:
    @staticmethod
    def fingertip_distance(landmarks, first: int = 0, second: int = 1) -> float:
        # Existing implementation
        pass
    
    @staticmethod
    def distance_to_volume(distance: float, min_dist: float, max_dist: float, steps: int) -> int:
        """
        Convert distance to volume step (0-steps)
        distance: 0.05 -> step 0 (mute)
        distance: 0.3 -> step 20 (max)
        """
        # Clamp distance to range
        # Calculate linear step
        pass
    
    @staticmethod
    def get_volume_threshold(current_volume: int, steps: int) -> int:
        """Get 5% threshold increment for volume"""
        return max(1, steps // 20)  # 5% of 20 steps = 1
```

---

## Phase 5: Server Integration (REFACTOR)

### 5.1 Update `src/media/Server.py`

**In `__init__`:**
```python
self.distance_tracker = DistanceGestureTracker()
self.gesture_config = load_gesture_config('src/gesture/gesture_config.json')
```

**In main command loop:**
- Check if command is "listen" → activate distance gesture tracking
- When gesture detected from Landmarker:
  - Pass to `distance_tracker.process_frame()`
  - If returns distance command, handle appropriately
  - Otherwise handle as normal command

---

## Phase 6: Landmarker Updates (REFACTOR)

### 6.1 Update `src/gesture/Landmarker.py`

**Changes:**
1. Load poses and commands from `gesture_config.json` instead of hardcoded dicts
2. Pass hand_landmarks to queue along with pose (needed for distance calculations)
3. Keep gesture detection logic unchanged for now

**Message format (queue):**
```python
command_queue.put({
    'type': 'gesture',
    'pose': 'peace',
    'hand_landmarks': hand_landmarks,  # NEW
    'hand_index': 0  # which hand (for multi-hand support)
})
```

---

## Phase 7: Full Execution Flow

### 7.1 Distance Gesture Sequence (Complete Example)

**Setup:**
1. User makes Shaka gesture
2. Server receives "listen" command
3. `distance_tracker` enters `WAITING_FOR_TRIGGER` state
4. Activation window: 5 seconds

**Execution:**
1. User makes Peace sign
2. `distance_tracker` detects "peace" is a distance gesture trigger
3. Enters `STABILIZING` state (0.5 second wait)
4. After 0.5s, enters `TRACKING` state
5. For next 2 seconds:
   - Every frame: Calculate distance between index (8) and thumb (4)
   - If distance crosses 5% threshold from last sent:
     - Calculate new volume step (0-20)
     - Send volume command to client
     - Track last sent volume
6. After 2 seconds or hand moves out of frame:
   - Enter `COMPLETE` state
   - Entire sequence is "one command" (counted as single gesture per shaka)
   - Return to `IDLE`, waiting for next shaka

**Volume Command Format:**
```python
{
    'type': 'command',
    'command': 'set_volume',
    'value': 12,  # 0-20 steps
    'percentage': 60  # For client reference (0-100)
}
```

---

## Phase 8: Reusability Framework

### 8.1 Future Distance Gestures
Define new distance gestures by adding to `gesture_config.json`:

```json
"rock_on": {
  "window_duration": 3,
  "stabilization_wait": 0.5,
  "command_type": "playback_speed",
  "finger_indices": [8, 12],
  "distance_range": [0.05, 0.4],
  "steps": 5,
  "speeds": [0.5, 0.75, 1.0, 1.25, 1.5]
}
```

Then `DistanceGestureTracker` and `GestureUtils` handle it generically.

### 8.2 New Command Types
Add handlers in Server's command processing:
```python
elif cmd['type'] == 'set_volume':
    send_to_client({'type': 'command', 'command': 'set_volume', 'value': cmd['value']})
elif cmd['type'] == 'set_playback_speed':
    send_to_client({'type': 'command', 'command': 'set_speed', 'value': cmd['value']})
```

---

## Implementation Checklist

### Phase 1: Configuration
- [ ] Create `gesture_config.json`
- [ ] Add gesture constants file reference

### Phase 2: GestureSequence
- [ ] Add `activate()`, `is_active()`, `can_send_command()`, `record_command()`, `deactivate()` methods

### Phase 3: Distance Tracker
- [ ] Create `DistanceGestureTracker.py`
- [ ] Implement state machine
- [ ] Implement timing logic (0.5s stabilization, 2s tracking)
- [ ] Implement threshold crossing detection

### Phase 4: Distance Utils
- [ ] Add `distance_to_volume()` method
- [ ] Add `get_volume_threshold()` method

### Phase 5: Server Integration
- [ ] Initialize distance_tracker and load config
- [ ] Update command handling to route distance gestures
- [ ] Add volume command handler

### Phase 6: Landmarker Updates
- [ ] Load gestures from config
- [ ] Pass hand_landmarks in queue messages
- [ ] Test gesture detection still works

### Phase 7: Testing
- [ ] Test single gesture (shaka → palm)
- [ ] Test distance gesture sequence (shaka → peace → volume)
- [ ] Test 5% threshold sending (not every frame)
- [ ] Test stabilization wait (0.5s)
- [ ] Test tracking window (2s)
- [ ] Test reset after sequence

### Phase 8: Documentation
- [ ] Update ARCHITECTURE.md
- [ ] Document gesture config format
- [ ] Document how to add new distance gestures

---

## Technical Notes

### Timing Considerations
- Landmarker runs ~20-30 FPS (camera dependent)
- 0.5s stabilization = ~10-15 frames
- 2s tracking = ~40-60 frames
- 5% threshold filtering prevents network overload

### Distance Calculation
- Normalized coordinates (0.0-1.0 range from MediaPipe)
- Euclidean distance = sqrt((x2-x1)² + (y2-y1)²)
- Range 0.05-0.3 maps to 20 volume steps linearly

### State Machine Safety
- Always return to IDLE if sequence times out
- Clear tracking data when state changes
- Prevent command sending if window expired

---

## Design Decisions (Finalized)

1. **Per-server configuration:** Distance gestures are configured per server instance. Each client has its own server running, so each user controls their own media independently. Server has independent distance_tracker per client connection is NOT needed—one tracker per server is sufficient.

2. **Hand out-of-frame behavior:** If hand leaves frame during tracking:
   - DO NOT reset to IDLE
   - Keep tracking window active
   - Hold last known volume value
   - If hand re-enters frame within tracking window (2s), resume distance tracking from current position
   - Only reset if window expires OR hand stays out for entire 2s window

3. **Debug logging:** Print state transitions for troubleshooting:
   ```
   [DISTANCE_TRACKER] State: IDLE → WAITING_FOR_TRIGGER (shaka detected)
   [DISTANCE_TRACKER] State: WAITING_FOR_TRIGGER → STABILIZING (peace detected, stabilizing 0.5s)
   [DISTANCE_TRACKER] State: STABILIZING → TRACKING (stabilization complete)
   [DISTANCE_TRACKER] Distance tracking: 0.15 → volume step 10
   [DISTANCE_TRACKER] Hand out of frame (0.3s of 2s window remaining)
   [DISTANCE_TRACKER] Hand re-entered frame, resuming track
   [DISTANCE_TRACKER] State: TRACKING → COMPLETE (2s window expired)
   [DISTANCE_TRACKER] State: COMPLETE → IDLE (waiting for next shaka)
   ```

