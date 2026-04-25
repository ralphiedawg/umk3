# UMK3 -- The third iteration of the universal media kontroller
## General Purpose
I'm always listening to music or watching youtube on another PC. Instead of having to find the keyboard that I move off of my desk to make space for my laptop, I want to control the media hands-free, via gestures.
(Robust KDE Connect but gesture-driven)
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
    - [ ] Server-Client Agnostic (Separate Classes but single script via args)
    - [ ] Periodic Heartbeat/Pinging (Once every 10s should be fine)
        - [x] Hearbeat Framework/Basic Layout?
        - [ ] How to find out whether media is currently playing, not just paused?
            - [ ] Macos: nowplaying-cli
            - [ ] Windows: `GlobalSystemMediaTransportControlsSessionManager`
            - [ ] Linux: `MPRIS` Over DBUS
            - [ ] Firefox/Chrome extension to create an interface for media controls?
        - [x] Client Loop For Heartbeat
            - [x] Multi-Threading
                - [x] One Thread to Send Heartbeat
                - [x] Another to Listen for Commands
    - [ ] Device Discovery -- Zeroconf (Bonjour)
    - [x] Turn Simple Server-Client into One Server, multiple clients -- KNET
- [x] Gesture Identification
    - [x] Basic Hand Landmarking
    - [x] Calculate Current Hand Gesture
        - [x] Shaka to wake,
        - [x] V for volume,
        - [x] Palm for play/pause
- [ ] Tray APP
    - [ ] Killswitch
    - [ ] Set Gesture Server Device

(Can you tell I'm used to java OOP?)
