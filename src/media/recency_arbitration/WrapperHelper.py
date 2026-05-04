from src.media.recency_arbitration.MacOSWrapper import MacOSWrapper
import platform

class WrapperHelper:
    def agnostic_media_status(self):
        os = platform.system()
        if os == 'Darwin':
            if MacOSWrapper.is_playing():
                return True
            return False
        elif os == 'Windows':
            # Call Windows Wrapper
            pass
