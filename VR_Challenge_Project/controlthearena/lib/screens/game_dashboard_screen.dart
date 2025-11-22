import 'package:controlthearena/core/models/game_state.dart';
import 'package:controlthearena/core/widgets/control_buttons.dart';
import 'package:controlthearena/core/widgets/status_bar.dart';
import 'package:flutter/material.dart';

import '../services/game_socket_service.dart';

class GameDashboardScreen extends StatefulWidget {
  const GameDashboardScreen({super.key});

  @override
  State<GameDashboardScreen> createState() => _GameDashboardScreenState();
}

class _GameDashboardScreenState extends State<GameDashboardScreen> {
  final GameSocketService socket = GameSocketService();

  GameState? _gameState;
  String _rawLastMessage = '';

  @override
  void initState() {
    super.initState();

    socket.onMessage = (data) {
      setState(() {
        _rawLastMessage = data.toString();

        final type = data['type'];

        if (type == 'state_update' || type == 'game_over') {
          final stateJson = data['state'] ?? {};
          _gameState = GameState.fromJson(Map<String, dynamic>.from(stateJson));
        }
      });
    };
  }

  void _sendAction(String action) {
    socket.sendInput(action);
  }

  @override
  void dispose() {
    socket.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Controller")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            StatusBar(state: _gameState),
            const SizedBox(height: 16),
            Text(
              'Last message: $_rawLastMessage',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const Spacer(),
            Center(
              child: ControlButtons(
                onLeft: () => _sendAction("move_left"),
                onRight: () => _sendAction("move_right"),
                onJump: () => _sendAction("jump"),
                onShoot: () => _sendAction("shoot"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
