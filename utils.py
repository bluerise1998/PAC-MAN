"""Fonctions utilitaires partagées (Maths & Physique)."""

from __future__ import annotations

import os
import sys
from collections import deque

from ecs.components import GridPosition
from maze.constants import (
    WALL_BOTTOM,
    WALL_LEFT,
    WALL_RIGHT,
    WALL_TOP,
    WINDOW_H,
    WINDOW_W,
)

# Marge en haut de l'écran pour afficher le score (en pixels)
TOP_MARGIN = 50


def resource_path(relative_path: str) -> str:
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def grid_to_pixel(row: int, col: int, cols: int, rows: int) -> tuple[int, int]:
    """Convertit les coordonnées GRILLE (Logique)
    en coordonnées PIXELS (Écran).

    Args:
        row: Numéro de ligne de la case.
        col: Numéro de colonne de la case.
        cols: Nombre total de colonnes du labyrinthe.
        rows: Nombre total de lignes du labyrinthe.

    Returns:
        tuple[int, int]: Position (x, y) en pixels sur l'écran.
    """
    # 1. On calcule la taille d'une seule case en pixels
    # On soustrait la marge de la hauteur disponible
    # pour ne pas sortir de l'écran
    cell_w = (WINDOW_W - 1) // cols
    cell_h = (WINDOW_H - 1 - TOP_MARGIN) // rows

    # 2. On calcule où se trouve le CENTRE de cette case sur l'écran
    # col * cell_w : Trouve la coord pixel du début de la col (coin gauche).
    # cell_w // 2  : Ajoute la moitié de la taille de la case pour se centrer.
    # On ajoute TOP_MARGIN à Y pour tout décaler vers le bas.
    return col * cell_w + cell_w // 2, row * cell_h + cell_h // 2 + TOP_MARGIN


def try_move_entity(
    gpos: GridPosition, direction: str, maze: list[list[int]]
) -> bool:
    """
    Tente de déplacer une entité dans une direction donnée.

    Vérifie les collisions avec les murs en utilisant des opérations bit-à-bit.

    Args:
        gpos (GridPosition): La position à modifier (mutable).
        direction (str): "UP", "DOWN", "LEFT" ou "RIGHT".
        maze (list): La grille du labyrinthe.

    Returns:
        bool: True si le déplacement a été effectué, False si bloqué.
    """
    cell = maze[gpos.row][gpos.col]
    moved = False

    # NOTE SUR LES MASQUES BINAIRES (&) :
    # La var 'cell' contient tous les murs mélangés (ex: 3 = Haut + Droite).
    # On use '&' pour ISOLER le mur qui nous intéresse et ignorer les autres.
    # Ex: (3 & WALL_TOP) -> (0011 & 0001) = 0001 (Vrai, il y a un mur).
    if direction == "UP" and not (cell & WALL_TOP):
        gpos.row -= 1
        moved = True
    elif direction == "RIGHT" and not (cell & WALL_RIGHT):
        gpos.col += 1
        moved = True
    elif direction == "DOWN" and not (cell & WALL_BOTTOM):
        gpos.row += 1
        moved = True
    elif direction == "LEFT" and not (cell & WALL_LEFT):
        gpos.col -= 1
        moved = True

    return moved


def get_bfs_direction(
    start_gpos: GridPosition,
    target_gpos: GridPosition,
    maze: list[list[int]],
    cols: int,
    rows: int,
) -> str | None:
    """Calcule la première direction à prendre
    pour le chemin le plus court (BFS).

    Args:
        start_gpos: Position de départ sur la grille.
        target_gpos: Position cible sur la grille.
        maze: La grille du labyrinthe (liste 2D d'entiers bitmask).
        cols: Nombre de colonnes du labyrinthe.
        rows: Nombre de lignes du labyrinthe.

    Returns:
        str | None: La direction ("UP", etc.) ou None si pas de chemin.
    """
    start = (start_gpos.row, start_gpos.col)
    target = (target_gpos.row, target_gpos.col)

    # File d'attente : stocke ( (row, col), Première_Direction_Prise )
    queue: deque[tuple[tuple[int, int], str | None]] = deque([(start, None)])
    visited = {start}

    while queue:
        # On retire l'élément le plus ANCIEN de la file
        # (FIFO - First In First Out).
        # .popleft() est spécifique à deque et est instantané (O(1)).
        # Une liste classique n'a pas popleft() et son pop(0) est lent.
        (curr_r, curr_c), first_dir = queue.popleft()

        # Cible trouvée : on retourne la 1ère direction
        if (curr_r, curr_c) == target:
            return first_dir

        cell = maze[curr_r][curr_c]

        # Définition des voisins : (delta_row, delta_col, Nom, Masque_Mur)
        neighbors = [
            (-1, 0, "UP", WALL_TOP),
            (0, 1, "RIGHT", WALL_RIGHT),
            (1, 0, "DOWN", WALL_BOTTOM),
            (0, -1, "LEFT", WALL_LEFT),
        ]

        for dr, dc, dir_name, wall_mask in neighbors:
            # Vérification bit-à-bit : Si le mur n'existe pas
            if not (cell & wall_mask):
                next_r, next_c = curr_r + dr, curr_c + dc

                if (next_r, next_c) not in visited:
                    visited.add((next_r, next_c))
                    if first_dir is not None:
                        # Si on a DÉJÀ une "première direction"
                        # (on est loin du départ),
                        # on la garde ! On ne l'écrase surtout pas.
                        new_first_dir = first_dir
                    else:
                        # Si first_dir est None (on est sur la case de départ),
                        # alors la direction qu'on prend
                        # MAINTENANT est la "première".
                        new_first_dir = dir_name

                    # On ajoute cette nouvelle étape à la file
                    # pour l'explorer plus tard.
                    # Si ce chemin est une impasse,
                    # il s'éteindra tout seul ici
                    # (pas d'ajout),
                    # et la boucle while passera
                    # automatiquement aux autres chemins
                    # en attente.
                    queue.append(((next_r, next_c), new_first_dir))

    return None  # Pas de chemin trouvé


def get_valid_directions(
    gpos: GridPosition, maze: list[list[int]]
) -> list[str]:
    """Retourne la liste des directions possibles depuis une case.

    Args:
        gpos: Position sur la grille à analyser.
        maze: La grille du labyrinthe (liste 2D d'entiers bitmask).

    Returns:
        list[str]: Liste des directions valides
            ("UP", "DOWN", "LEFT", "RIGHT").
    """
    cell = maze[gpos.row][gpos.col]
    valid = []
    if not (cell & WALL_TOP):
        valid.append("UP")
    if not (cell & WALL_RIGHT):
        valid.append("RIGHT")
    if not (cell & WALL_BOTTOM):
        valid.append("DOWN")
    if not (cell & WALL_LEFT):
        valid.append("LEFT")
    return valid
