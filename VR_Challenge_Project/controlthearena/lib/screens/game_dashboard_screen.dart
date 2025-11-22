import 'package:controlthearena/core/widgets/control_buttons.dart';
import 'package:flutter/material.dart';
import '../services/game_socket_service.dart';

class GameDashboardScreen extends StatefulWidget {
  const GameDashboardScreen({super.key});

  @override
  State<GameDashboardScreen> createState() => _GameDashboardScreenState();
}

class _GameDashboardScreenState extends State<GameDashboardScreen> {
  final GameSocketService socket = GameSocketService();
  String lastState = "Waiting...";

  @override
  void initState() {
    super.initState();

    // Listen to messages coming from Python
    socket.onMessage = (data) {
      setState(() {
        lastState = data.toString();
      });
    };
  }

  void send(String action) {
    socket.sendInput(action);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Controller")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text("State: $lastState"),
            const SizedBox(height: 20),

            ControlButtons(
              onLeft: () => send("move_left"),
              onRight: () => send("move_right"),
              onJump: () => send("jump"),
              onShoot: () => send("shoot"),
            ),
          ],
        ),
      ),
    );
  }
}
