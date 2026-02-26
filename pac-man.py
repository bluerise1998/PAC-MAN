import pygame
import sys

from parser.parser import init_config
from screens.game import run_game
from screens.highscores import run_highscores
from screens.instructions import run_instruction
from screens.menu import run_menu


def create_window() -> pygame.Surface:
    """
    Initialise Pygame et crée la fenêtre principale.

    Returns:
        pygame.Surface: La surface principale sur laquelle on dessine.
    """
    # Initialise tous les modules internes de Pygame (Son, Vidéo, Events...)
    pygame.init()
    # Crée la fenêtre graphique de taille 800x600 pixels.
    surface = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pac Man")
    return surface


def game_loop(surface: pygame.Surface) -> None:
    """Boucle principale de l'application qui gère la navigation entre écrans.

    Args:
        surface: La surface principale Pygame sur laquelle dessiner.
    """
    page = "menu"
    while page != "Exit":
        if page == "menu":
            page = run_menu(surface, page)
        elif page == "Start Game":
            page = run_game(surface, page)
        elif page == "View Highscores":
            page = run_highscores(surface, page)
        elif page == "Instructions":
            page = run_instruction(surface, page)
    pygame.quit()


def main() -> None:
    """Run the game, printing the loaded config before starting."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    init_config(config_path)
    surface = create_window()
    game_loop(surface)


if __name__ == "__main__":
    main()
