import 'package:flutter/material.dart';

class ControlButtons extends StatelessWidget {
  final VoidCallback onLeft;
  final VoidCallback onRight;
  final VoidCallback onJump;
  final VoidCallback onShoot;

  const ControlButtons({
    super.key,
    required this.onLeft,
    required this.onRight,
    required this.onJump,
    required this.onShoot,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(onPressed: onJump, child: const Text("Jump")),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(onPressed: onLeft, child: const Text("Left")),
            const SizedBox(width: 20),
            ElevatedButton(onPressed: onRight, child: const Text("Right")),
          ],
        ),
        const SizedBox(height: 12),
        ElevatedButton(onPressed: onShoot, child: const Text("Shoot")),
      ],
    );
  }
}
