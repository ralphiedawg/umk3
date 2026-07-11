import asyncio
import websockets
from websockets.asyncio.server import ServerConnection
import json

async def handle_commands(websocket: ServerConnection):
    try:
        print('Client ready and accepting commands')
        while True:
            cmd = input('command: ')
            command = {
                'type': f'{cmd}',
                'increment': ''
            }
            await websocket.send(json.dumps(command))
    except Exception as e:
        print(f'Error {e} occurred, closing connection')
        await websocket.close()


async def main():
    async with websockets.serve(handle_commands, 'localhost', 2023):
        await asyncio.Future()

asyncio.run(main())
