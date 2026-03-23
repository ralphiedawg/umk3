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
    - [ ] Simple communication between devices over LAN
    - [ ] Periodic Heartbeat (Once every 10s should be fine)
        - [ ] Determine during heartbeat whether device is playing media
- [ ] Gesture Identification
