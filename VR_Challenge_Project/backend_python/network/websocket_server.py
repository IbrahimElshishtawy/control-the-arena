import asyncio
import websockets # type: ignore

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8765):
       await asyncio.Future()  # Keep the server running
 # Keep the server running

async def handler(websocket, path):
    # Your WebSocket logic here
    pass

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped.")

