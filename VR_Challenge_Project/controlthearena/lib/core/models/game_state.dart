class PlayerState {
  final int x;
  final int y;
  final int hp;

  PlayerState({required this.x, required this.y, required this.hp});

  factory PlayerState.fromJson(Map<String, dynamic> json) {
    return PlayerState(
      x: json['x'] ?? 0,
      y: json['y'] ?? 0,
      hp: json['hp'] ?? 100,
    );
  }
}

class GameState {
  final int score;
  final int level;
  final PlayerState player;
  final bool isGameOver;

  GameState({
    required this.score,
    required this.level,
    required this.player,
    required this.isGameOver,
  });

  factory GameState.fromJson(Map<String, dynamic> json) {
    return GameState(
      score: json['score'] ?? 0,
      level: json['level'] ?? 1,
      player: PlayerState.fromJson(json['player'] ?? {}),
      isGameOver: json['is_game_over'] ?? false,
    );
  }
}
