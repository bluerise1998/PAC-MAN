"""Écran de Game Over — affiche le score, puis demande le pseudo."""

import pygame

from maze.constants import WINDOW_W, WINDOW_H

MAX_LENGTH = 10


def _wait_for_key(
    surface: pygame.Surface,
    game_over_text: pygame.Surface,
    score_text: pygame.Surface,
    center_x: int, center_y: int,
) -> str | None:
    """Affiche GAME OVER + score et attend une touche.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        game_over_text: Surface du texte "GAME OVER" pré-rendu.
        score_text: Surface du texte de score pré-rendu.
        center_x: Position X du centre de l'écran.
        center_y: Position Y du centre de l'écran.

    Returns:
        str | None: "Exit" si fermeture demandée, None si touche pressée.
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Exit"
            if event.type == pygame.KEYDOWN:
                return None

        surface.fill((0, 0, 0))
        rect = game_over_text.get_rect(
            center=(center_x, center_y - 50)
        )
        surface.blit(game_over_text, rect)
        rect = score_text.get_rect(
            center=(center_x, center_y + 40)
        )
        surface.blit(score_text, rect)
        pygame.display.flip()


def _ask_username(
    surface: pygame.Surface, center_x: int, center_y: int,
) -> tuple[str | None, str]:
    """Saisie du pseudo : lettres uniquement, 1-10 caractères.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        center_x: Position X du centre de l'écran.
        center_y: Position Y du centre de l'écran.

    Returns:
        tuple[str | None, str]: ("Exit", "") si fermeture,
            (None, pseudo) sinon.
    """
    pseudo = ""
    font_title = pygame.font.Font(None, 60)
    font_input = pygame.font.Font(None, 50)
    font_hint = pygame.font.Font(None, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Exit", ""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(pseudo) >= 1:
                    return None, pseudo
                if event.key == pygame.K_BACKSPACE:
                    pseudo = pseudo[:-1]
                elif len(pseudo) < MAX_LENGTH and event.unicode.isalpha():
                    pseudo += event.unicode.upper()

        surface.fill((0, 0, 0))

        title = font_title.render("Enter your name", True, (255, 255, 0))
        surface.blit(title, title.get_rect(center=(center_x, center_y - 100)))

        display_text = pseudo if pseudo else "_"
        color = (255, 255, 255) if pseudo else (100, 100, 100)
        input_text = font_input.render(display_text, True, color)
        rect = input_text.get_rect(
            center=(center_x, center_y)
        )
        surface.blit(input_text, rect)

        hint = font_hint.render(
            "Letters only (1-10) — Enter to confirm",
            True, (150, 150, 150),
        )
        surface.blit(hint, hint.get_rect(center=(center_x, center_y + 60)))

        pygame.display.flip()


def run_game_over(surface: pygame.Surface, score: int) -> tuple[str, str]:
    """Game Over : attend une touche puis saisie pseudo.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        score: Le score final du joueur.

    Returns:
        tuple[str, str]: (page suivante, pseudo saisi).
    """
    font_big = pygame.font.Font(None, 100)
    font_small = pygame.font.Font(None, 50)

    game_over_text = font_big.render("GAME OVER", True, (255, 0, 0))
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))

    center_x = WINDOW_W // 2
    center_y = WINDOW_H // 2

    # Étape 1 : Afficher GAME OVER
    result = _wait_for_key(
        surface, game_over_text, score_text,
        center_x, center_y,
    )
    if result == "Exit":
        return "Exit", ""

    # Étape 2 : Saisie du pseudo
    result, pseudo = _ask_username(surface, center_x, center_y)
    if result == "Exit":
        return "Exit", ""

    return "menu", pseudo


def run_winner(surface: pygame.Surface, score: int) -> tuple[str, str]:
    """Victoire : attend une touche puis saisie pseudo.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        score: Le score final du joueur.

    Returns:
        tuple[str, str]: (page suivante, pseudo saisi).
    """
    font_big = pygame.font.Font(None, 100)
    font_small = pygame.font.Font(None, 50)

    winner_text = font_big.render("WINNER !", True, (0, 255, 0))
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))

    center_x = WINDOW_W // 2
    center_y = WINDOW_H // 2

    # Étape 1 : Afficher WINNER
    result = _wait_for_key(
        surface, winner_text, score_text,
        center_x, center_y,
    )
    if result == "Exit":
        return "Exit", ""

    # Étape 2 : Saisie du pseudo
    result, pseudo = _ask_username(surface, center_x, center_y)
    if result == "Exit":
        return "Exit", ""

    return "menu", pseudo
