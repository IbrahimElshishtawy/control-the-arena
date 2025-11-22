import json


def encode_message(message: dict) -> str:
  """
  يحوّل dict إلى JSON string عشان نبعته على الـ WebSocket.
  """
  return json.dumps(message)


def decode_message(raw: str) -> dict:
  """
  يحوّل JSON string إلى dict.
  لو الرسالة مش JSON مظبوط يرجع dict فاضي.
  """
  try:
    return json.loads(raw)
  except json.JSONDecodeError:
    return {}


def make_state_update_payload(state_dict: dict) -> dict:
  return {
    "type": "state_update",
    "state": state_dict,
  }


def make_ack(message: str) -> dict:
  return {
    "type": "ack",
    "message": message,
  }


def make_error(message: str) -> dict:
  return {
    "type": "error",
    "message": message,
  }


def make_game_over_payload(state_dict: dict) -> dict:
  return {
    "type": "game_over",
    "state": state_dict,
  }
