from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus
)


class WindowsWrapper:
    def __init__(self):
        pass

    @staticmethod
    async def get_session_manager():
        """Get the global media transport controls session manager"""
        try:
            manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
            return manager
        except Exception as e:
            print(f"Error getting session manager: {e}")
            return None

    @staticmethod
    async def is_playing() -> bool:
        """Check if media is currently playing on the system"""
        try:
            manager = await WindowsWrapper.get_session_manager()
            if manager is None:
                return False

            # Get all sessions and check for any playing
            sessions = manager.get_sessions()
            for session in sessions:
                playback_info = session.get_playback_info()
                if playback_info is None:
                    continue
                
                status = playback_info.playback_status
                if status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING:
                    return True
            
            return False

        except Exception as e:
            print(f"Error checking playback status: {e}")
            return False


if __name__ == '__main__':
    import asyncio
    print(asyncio.run(WindowsWrapper.is_playing()))
