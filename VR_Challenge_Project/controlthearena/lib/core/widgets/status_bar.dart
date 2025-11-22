import 'package:flutter/material.dart';
import '../models/game_state.dart';

class StatusBar extends StatelessWidget {
  final GameState? state;

  const StatusBar({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    if (state == null) {
      return const Text(
        'Waiting for game state...',
        style: TextStyle(fontSize: 16),
      );
    }

    final player = state!.player;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Score: ${state!.score}', style: const TextStyle(fontSize: 18)),
        Text('Level: ${state!.level}', style: const TextStyle(fontSize: 16)),
        Text('HP: ${player.hp}', style: const TextStyle(fontSize: 16)),
        Text(
          'Position: (${player.x}, ${player.y})',
          style: const TextStyle(fontSize: 16),
        ),
        if (state!.isGameOver)
          const Padding(
            padding: EdgeInsets.only(top: 8.0),
            child: Text(
              'GAME OVER',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.red,
              ),
            ),
          ),
      ],
    );
  }
}
