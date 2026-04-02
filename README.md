# UMK3 --- The third iteration of the universal media kontroller
## General Purpose
I'm always listening to music or watching youtube on another PC. Instead of having to find the keyboard that I move off of my desk to make space for my laptop, I want to control the media hands-free, via gestures.
## Stack
- Fully Python
- Mediapipe for hand landmark detection, just math for gesture identification
- Pynput for media controls (skip, rewind, etc)
## Methodology
- On command, ensure that the media playing is focused, to for controls to work properly. 
- Which device playing media is handled thru a heartbeat system, most recent wins. 
- LAN ONLY!!

# TODO: 
- [x] github repo
- [x] Basic Media Control Framework
- [ ] Device Connection Framework
    - [x] Simple communication between devices over LAN
    - [ ] Periodic Heartbeat/Pinging (Once every 10s should be fine)
        - [ ] Determine during heartbeat whether device is playing media
    - [ ] Encryption? Not needed if not relaying currently playing media
- [ ] Gesture Identification
    - [ ] Basic Hand Landmarking
    - [ ] Calculate Current Hand Gesture
        - [ ] Shaka to wake
        - [ ] V for volume,
        - [ ] Palm for play/pause
- [ ] Tray APP
    - [ ] Killswitch
    - [ ] Set Gesture Server Device
