"""Écran des instructions."""

import pygame

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

INSTRUCTIONS_LINES = [
    "You are Pac-Man, a yellow character",
    "lost in a maze full of ghosts.",
    "Eat all the dots to complete the level.",
    "Avoid the ghosts or you lose a life.",
    "Eat a big dot to turn ghosts blue",
    "and eat them for bonus points!",
    "Controls:",
    "Arrow keys - Move Pac-Man",
    "Space - Pause",
    "C - Cheat mode",
    "N - Skip level",
    "Escape - Back to menu",
]


def draw_title(surface: pygame.Surface) -> None:
    """Dessine le titre 'Instructions' en jaune, centré en haut.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
    """
    font = pygame.font.Font(None, 60)
    title = font.render("Instructions", True, YELLOW)
    surface.blit(title, title.get_rect(center=(400, 60)))


def draw_instructions(surface: pygame.Surface) -> None:
    """Dessine les lignes d'instructions en blanc.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
    """
    font = pygame.font.Font(None, 28)
    # On boucle sur chaque ligne de texte pour les
    # afficher les unes sous les autres.
    # i sert à calculer le décalage vertical (Y) pour chaque ligne.
    for i, line in enumerate(INSTRUCTIONS_LINES):
        text = font.render(line, True, WHITE)
        surface.blit(text, text.get_rect(center=(400, 140 + i * 38)))


def draw_screen(surface: pygame.Surface) -> None:
    """Dessine tout l'écran instructions : titre + texte.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
    """
    draw_title(surface)
    draw_instructions(surface)


def handle_input(events: list[pygame.event.Event]) -> bool:
    """Vérifie si la touche Escape est pressée.

    Args:
        events: Liste des événements Pygame de la frame.

    Returns:
        bool: True si Escape est pressé, False sinon.
    """
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
    return False


def run_instruction(surface: pygame.Surface, page: str) -> str:
    """Boucle de l'écran instructions. Escape retourne au menu.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        page: Page courante (doit être "Instructions").

    Returns:
        str: La page suivante ("menu" ou "Exit").
    """
    while page == "Instructions":
        # Récupération des événements (clavier, souris)
        # depuis la dernière frame.
        events = pygame.event.get()

        # Gestion de la sortie (croix de la fenêtre)
        for event in events:
            if event.type == pygame.QUIT:
                return "Exit"

        # Si le joueur appuie sur Echap,
        # on change la page pour revenir au menu.
        if handle_input(events):
            page = "menu"

        # Effaçage de l'écran (Back Buffer)
        surface.fill((0, 0, 0))
        draw_screen(surface)
        # Affichage final (Flip)
        pygame.display.flip()

    return page
