import asyncio
import os
import sys

import websockets # type: ignore

# نضيف مسار backend_python للـ sys.path عشان نقدر نستورد config و game_engine
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
  sys.path.append(BASE_DIR)

from config import HOST, PORT  # type: ignore
from game_engine import GameEngine  # type: ignore
from network.protocol import (  # type: ignore
  encode_message,
  decode_message,
  make_state_update_payload,
  make_ack,
  make_error,
  make_game_over_payload,
)


class GameWebSocketServer:
  def __init__(self):
    self.engine = GameEngine()
    self.connected_clients: set[websockets.WebSocketServerProtocol] = set()

  async def handler(self, websocket):
    # عميل جديد
    self.connected_clients.add(websocket)
    print("Client connected")

    # ابعت ACK أول ما يتوصل
    await websocket.send(encode_message(make_ack("connected")))

    try:
      async for message in websocket:
        data = decode_message(message)
        await self.handle_message(websocket, data)
    except websockets.exceptions.ConnectionClosed:
      print("Client disconnected")
    finally:
      self.connected_clients.remove(websocket)

  async def handle_message(self, websocket, data: dict):
    msg_type = data.get("type")

    if msg_type == "handshake":
      # ممكن تخزن معلومات عن العميل هنا
      print("Handshake from client:", data)
      await websocket.send(encode_message(make_ack("handshake_ok")))

    elif msg_type == "input":
      action = data.get("action")
      if not action:
        await websocket.send(
          encode_message(make_error("missing_action"))
        )
        return

      print("Input received:", action)
      self.engine.handle_input(action)
      self.engine.update()

      state_dict = self.engine.get_state_dict()

      # لو في Game Over
      if state_dict.get("is_game_over"):
        payload = make_game_over_payload(state_dict)
      else:
        payload = make_state_update_payload(state_dict)

      await websocket.send(encode_message(payload))

    else:
      await websocket.send(
        encode_message(make_error("unknown_message_type"))
      )

  async def run(self):
    async with websockets.serve(self.handler, HOST, PORT):
      print(f"Server running on ws://{HOST}:{PORT}")
      await asyncio.Future()  # run forever


if __name__ == "__main__":
  server = GameWebSocketServer()
  asyncio.run(server.run())
