# UMK3 Architecture: Multi-Client Gesture Control

## Overview
UMK3 is a universal media controller that uses hand gesture recognition to control media playback across multiple rooms. A single server with a camera detects gestures and routes commands to the client device that has played media most recently.

## Current Issues
1. **Backwards Data Flow**: Client currently runs Landmarker and sends commands to Server
2. **No Multi-Client Support**: Only one connection possible; no heartbeat-based routing
3. **No Listen Mode**: All gestures trigger commands (no gating mechanism)

---

## Desired Architecture

### System Components

#### 1. **Server** (Gesture Detection & Command Routing)
- **Runs**: Hand gesture detection via `Landmarker.py`
- **Listens**: On port 2022 for incoming connections from multiple clients
- **Receives**: Periodic heartbeat messages from all connected clients
- **Tracks**: Which client most recently had media playing
- **Sends**: Gesture commands only to the active client
- **Enforces**: Listen mode before executing commands

#### 2. **Client** (Command Execution)
- **Connects**: To Server on startup (port 2022)
- **Sends**: Periodic heartbeats with device ID, timestamp, and playStatus
- **Receives**: Gesture commands from Server
- **Executes**: Media control commands via `media_controls.py` (keyboard press emulation)
- **Responds**: Acknowledgments back to Server

#### 3. **Heartbeat System**
- **Purpose**: Server determines which client to send commands to
- **Frequency**: Client sends heartbeat every N seconds
- **Content**: Device ID, timestamp, current playStatus ("Playing"/"Paused"/"Not Playing")
- **Logic**: Server tracks most recent client with playStatus="Playing"

#### 4. **Listen Mode** (Server-Side)
- **Activation**: Gesture `"open_palm"` detected
- **Duration**: 2-second window for next command
- **Behavior**: Commands only execute if within listen window
- **Reset**: After first command or timeout expires

---

## Data Flow

### Message Protocol

**Client → Server (Heartbeat)**
```json
{
  "type": "heartbeat",
  "device-id": 0,
  "timestamp": "Mon Apr 13 02:07:13 2025",
  "playStatus": "Playing"
}
```

**Server → Client (Command)**
```json
{
  "type": "command",
  "command": "pause",
  "timestamp": "Mon Apr 13 02:07:15 2025"
}
```

### Execution Flow

1. **Startup**
   - Server starts, initializes Landmarker, begins listening on port 2022
   - Client connects and spawns heartbeat sender thread

2. **Normal Operation**
   - Client sends heartbeat every 1-2 seconds
   - Server receives heartbeat, updates client's timestamp and playStatus
   - Server identifies active client (most recent playing)
   - Landmarker continuously detects gestures

3. **Gesture Detection**
   - Server detects hand gesture (e.g., "peace" = skip)
   - Checks if listen mode active
   - If valid: sends command to active client via socket
   - If not in listen window: ignores gesture

4. **Command Execution**
   - Client receives command from Server
   - Client calls `media_controls.send_cmd()`
   - Media control executes on client machine

---

## Implementation Roadmap

### Phase 1: Protocol & Data Structures
- [x] Update `Heartbeat.py`: Add `"type": "heartbeat"` to JSON output
- [ ] Update `Command.py`: Ensure clean command JSON format
- [ ] Update `Client.py`: Add client-side state tracking `(device_id, playStatus)`

### Phase 2: Server Multi-Client Support
- [ ] Refactor `Server.py`: Replace single connection with connection pool
  - Add `self.clients = {}` dictionary to track connected clients
  - Add `self.active_client_id` to track active routing target
  - Implement socket listener that accepts multiple connections
- [ ] Add heartbeat receiver: Parse incoming heartbeats, update active client

### Phase 3: Threading for Parallel Operations
- [ ] Add threading to `Server.py`:
  - Thread 1: Socket listener (accept connections + heartbeat parsing)
  - Thread 2: Gesture detection `(Landmarker.open_cam)`
- [ ] Add threading to `Client.py`:
  - Thread 1: Heartbeat sender (periodic)
  - Thread 2: Command listener (receive from server)

### Phase 4: Move Landmarker to Server
- [ ] Move `Landmarker.open_cam()` logic from Client to Server
- [ ] Update `Landmarker.py`: Remove `Client.recieve_command()` calls
- [ ] Integrate with gesture detection thread in Server
- [ ] Send commands to active client via socket instead of local execution

### Phase 5: Listen Mode
- [ ] Add state tracking to `Server.py`: `listening`, `listen_timestamp`, `listen_timeout`
- [ ] Implement in gesture thread: Check listen window before sending command

### Phase 6: Integration & Testing
- [ ] Update `main.py`: Server mode runs Landmarker, Client mode sends heartbeats
- [ ] Test multi-client scenarios (2+ devices in different rooms)
- [ ] Verify heartbeat-based routing works correctly
- [ ] Verify listen mode gates commands properly

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Server runs Landmarker** | Centralized gesture detection; single camera point |
| **Client sends heartbeats** | Server always knows which device is active without asking |
| **Listen mode server-side** | Prevents accidental commands; gating happens before network send |
| **Threading in both Server & Client** | Socket communication cannot block gesture/heartbeat operations |
| **Active client tracking** | Prevents controlling device in other room; routes to most recently active |

---

## Future Enhancements

- **Heartbeat Timeout**: Remove inactive clients from tracking after N seconds without heartbeat
- **Command Confirmation**: Client sends acknowledgment back to Server
- **Gesture Logging**: Track which gestures triggered which commands
- **Configuration File**: Set listen timeout, heartbeat frequency, port numbers
- **Web Dashboard**: View active clients and recent commands
