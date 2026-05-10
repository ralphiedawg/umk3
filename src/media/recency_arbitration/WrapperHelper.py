from src.media.recency_arbitration.MacOSWrapper import MacOSWrapper
from src.media.recency_arbitration.WindowsWrapper import WindowsWrapper
import platform
import asyncio

class WrapperHelper:
    @staticmethod
    def agnostic_media_status():
        os = platform.system()
        if os == 'Darwin':
            if MacOSWrapper.is_playing():
                return True
            return False
        elif os == 'Windows':
            return asyncio.run(WindowsWrapper.is_playing())
        elif os == 'Linux':
            # TODO: Implement Linux wrapper using MPRIS over DBUS
            pass
        return False

