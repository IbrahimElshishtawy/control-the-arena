import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as ws_status;

import '../core/constants/app_config.dart';

typedef OnMessage = void Function(Map<String, dynamic> data);

class GameSocketService {
  WebSocketChannel? _channel;
  OnMessage? onMessage;

  bool get isConnected => _channel != null;

  void connect() {
    if (_channel != null) return;

    _channel = WebSocketChannel.connect(Uri.parse(AppConfig.wsHost));

    print("Flutter Connected to Python WebSocket...");

    _channel!.stream.listen((event) {
      try {
        final decoded = jsonDecode(event);
        if (decoded is Map<String, dynamic>) {
          onMessage?.call(decoded);
        }
      } catch (e) {
        print("WebSocket decode error: $e");
      }
    });
  }

  void sendHandshake() {
    send({"type": "handshake", "device": "flutter_app"});
  }

  void sendInput(String action) {
    send({"type": "input", "action": action});
  }

  void send(Map<String, dynamic> data) {
    if (_channel == null) return;
    _channel!.sink.add(jsonEncode(data));
  }

  void disconnect() {
    if (_channel != null) {
      _channel!.sink.close(ws_status.goingAway);
      _channel = null;
      print("WebSocket Disconnected.");
    }
  }
}
