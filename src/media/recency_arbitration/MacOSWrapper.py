import asyncio

class MacOSWrapper:
    def __init__(self):
        pass
    @staticmethod
    async def run(cmd):
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout = asyncio.subprocess.PIPE,
            stderr = asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
            return stdout
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')
            return stderr

    @staticmethod
    def is_playing() -> bool:
        playback_rate = asyncio.run(MacOSWrapper.run('nowplaying-cli get playbackRate'))

        if playback_rate is None:
            return False
        if isinstance(playback_rate, bytes):
            playback_rate = playback_rate.decode()

        playback_rate = playback_rate.strip()
        if playback_rate not in ('null', '0', 0):
            return True
        return False

if __name__ == '__main__':
    print(MacOSWrapper.is_playing())
