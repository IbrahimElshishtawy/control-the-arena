# main.py
from core.game import Game
from scenes.main_menu import MainMenu

if __name__ == "__main__":
    game = Game(MainMenu)
    game.run()
