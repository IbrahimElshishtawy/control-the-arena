import 'package:controlthearena/screens/game_dashboard_screen.dart';
import 'package:flutter/material.dart';
import '../services/game_socket_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final GameSocketService socket = GameSocketService();

  String logText = "Not Connected";

  @override
  void initState() {
    super.initState();
    socket.onMessage = (data) {
      setState(() {
        logText = "Received: ${data.toString()}";
      });
    };
  }

  void _connect() {
    socket.connect();
    socket.sendHandshake();
    setState(() {
      Navigator.of(
        context,
      ).push(MaterialPageRoute(builder: (_) => const GameDashboardScreen()));
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Control The Arena")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: _connect,
              child: const Text("Connect to Python Server"),
            ),
            const SizedBox(height: 20),
            Text(logText, style: const TextStyle(fontSize: 16)),
          ],
        ),
      ),
    );
  }
}
