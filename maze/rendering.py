"""Affichage du labyrinthe."""

import pygame

from maze.constants import (
    BLUE,
    WALL_BOTTOM,
    WALL_LEFT,
    WALL_RIGHT,
    WALL_TOP,
    WINDOW_H,
    WINDOW_W,
)
from utils import TOP_MARGIN


def draw_maze(
    surface: pygame.Surface, maze: list[list[int]],
    cols: int, rows: int,
) -> None:
    """
    Parcourt la grille du labyrinthe et dessine les murs.

    Chaque cellule contient un entier qui est un masque binaire.
    Exemple: Si cell = 5 (0101 binaire), cela signifie
    WALL_TOP (1) + WALL_BOTTOM (4).
    """
    # On calcule la largeur et hauteur d'une seule case en pixels
    # On prend en compte la marge haute
    cell_w = (WINDOW_W - 1) // cols
    cell_h = (WINDOW_H - 1 - TOP_MARGIN) // rows

    for row in range(rows):
        for col in range(cols):
            # Position en pixels du coin haut-gauche de la case
            x = col * cell_w
            y = row * cell_h + TOP_MARGIN

            # La valeur de la case (ex: 9 = 1001 en binaire = Haut + Gauche)
            cell = maze[row][col]

            # Si la case est un bloc plein (15 = 1111),
            # c'est le "42" ou un mur.
            # On la remplit en blanc.
            if cell == 15:
                pygame.draw.rect(
                    surface, (135, 206, 235), (x, y, cell_w, cell_h)
                )

            # Vérification bit-à-bit (&) pour chaque mur possible
            if cell & WALL_TOP:  # Si le bit 1 est là -> Mur en HAUT
                # Tuple 1 (x, y) : Point de départ (Coin Haut-Gauche)
                # Tuple 2 (x + cell_w, y) : Point d'arrivée (Coin Haut-Droite)
                pygame.draw.line(surface, BLUE, (x, y), (x + cell_w, y))
            if cell & WALL_RIGHT:  # Mur à DROITE
                # De Haut-Droite (x+w, y) vers Bas-Droite (x+w, y+h)
                pygame.draw.line(
                    surface, BLUE, (x + cell_w, y), (x + cell_w, y + cell_h)
                )
            if cell & WALL_BOTTOM:  # Mur en BAS
                # De Bas-Gauche (x, y+h) vers Bas-Droite (x+w, y+h)
                pygame.draw.line(
                    surface, BLUE, (x, y + cell_h), (x + cell_w, y + cell_h)
                )
            if cell & WALL_LEFT:  # Mur à GAUCHE
                # De Haut-Gauche (x, y) vers Bas-Gauche (x, y+h)
                pygame.draw.line(surface, BLUE, (x, y), (x, y + cell_h))
