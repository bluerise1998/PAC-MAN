"""Écran Highscores — affiche les 4 meilleurs scores."""

from __future__ import annotations

from typing import Any

import pygame
import json
import os
from maze.constants import WINDOW_W
from parser.parser import config

MAX_SCORES = 10


def _is_valid_entry(entry: Any) -> bool:
    """Vérifie qu'une entrée de highscore est valide.

    Args:
        entry: L'objet à valider.

    Returns:
        bool: True si l'entrée a un "name" (lettres,
            1-10 car.) et un "score" (0-1000000).
    """
    if not isinstance(entry, dict):
        return False
    if set(entry.keys()) != {"name", "score"}:
        return False
    name = entry["name"]
    score = entry["score"]
    if (not isinstance(name, str)
            or not name.isalpha()
            or not 1 <= len(name) <= 10):
        return False
    if not isinstance(score, int) or not 0 <= score <= 1000000:
        return False
    return True


def load_highscores() -> list[dict[str, Any]]:
    """Charge la liste des meilleurs scores depuis le fichier JSON.

    Returns:
        list[dict[str, Any]]: Liste de dicts
            [{"name": ..., "score": ...}, ...].
    """
    filename = config["highscore_filename"]
    if not os.path.exists(filename):
        return []
    try:
        with open(filename) as f:
            data = json.load(f)
    except (ValueError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [entry for entry in data if _is_valid_entry(entry)]


def save_highscore(name: str, score: int) -> None:
    """Ajoute un score au classement et sauvegarde dans le fichier.

    Args:
        name: Pseudo du joueur.
        score: Score obtenu.
    """
    filename = config["highscore_filename"]
    scores = load_highscores()
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:MAX_SCORES]
    with open(filename, "w") as f:
        json.dump(scores, f, indent=2)


def get_best_score() -> int:
    """Retourne le meilleur score pour l'affichage en jeu.

    Returns:
        int: Le meilleur score, ou 0 si aucun score enregistré.
    """
    scores = load_highscores()
    if scores:
        return int(scores[0]["score"])
    return 0


def run_highscores(surface: pygame.Surface, page: str) -> str:
    """Affiche le tableau des highscores.
    Echap ou une touche pour revenir au menu.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        page: Page courante (doit être "View Highscores").

    Returns:
        str: La page suivante ("menu" ou "Exit").
    """
    font_title = pygame.font.Font(None, 74)
    font_subtitle = pygame.font.Font(None, 50)
    font_score = pygame.font.Font(None, 42)

    scores = load_highscores()
    center_x = WINDOW_W // 2

    while page == "View Highscores":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Exit"
            if event.type == pygame.KEYDOWN:
                return "menu"

        surface.fill((0, 0, 0))

        # Titre "PAC MAN" en jaune
        title = font_title.render("PAC MAN", True, (255, 255, 0))
        surface.blit(title, title.get_rect(center=(center_x, 80)))

        # Sous-titre "Highscores:"
        subtitle = font_subtitle.render("Highscores:", True, (255, 255, 255))
        surface.blit(subtitle, subtitle.get_rect(center=(center_x, 170)))

        # Liste des scores
        if not scores:
            no_score = font_score.render(
                "No scores yet", True, (150, 150, 150)
            )
            surface.blit(no_score, no_score.get_rect(center=(center_x, 260)))
        else:
            for i, entry in enumerate(scores):
                if i == 4:
                    break
                line = f"{i + 1}. {entry['name']} - {entry['score']}"
                color = (255, 255, 0) if i == 0 else (255, 255, 255)
                text = font_score.render(line, True, color)
                rect = text.get_rect(
                    center=(center_x, 260 + i * 60)
                )
                surface.blit(text, rect)

        pygame.display.flip()

    return page
