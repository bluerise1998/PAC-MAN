from __future__ import annotations

from typing import Any

import esper

from ecs.components import (
    Dot,
    GameOver,
    Ghost,
    GridPosition,
    Invincible,
    Lives,
    Player,
    Position,
    PowerPellet,
    Respawning,
    Score,
    TimeUp,
    Timer,
    Vulnerable,
)
from parser.parser import config
from utils import grid_to_pixel


def get_player_info() -> tuple[
    int, GridPosition, Position, Score,
] | None:
    """Récupère l'entité, la position grille, la position pixel
    et le score du joueur.

    Returns:
        tuple | None: (ent, GridPosition, Position, Score)
            ou None si pas de joueur.
    """
    for ent, (gpos, pos, score, _player) in esper.get_components(
        GridPosition, Position, Score, Player
    ):
        return ent, gpos, pos, score
    return None


def check_dot_collisions(player_pos: Position, player_score: Score) -> None:
    """Gère la consommation des gommes (Dots).

    Args:
        player_pos: Position pixel du joueur.
        player_score: Composant Score du joueur (muté en place).
    """
    # On utilise la Position (pixels) pour une collision visuelle précise
    points_per_pacgum = config["points_per_pacgum"]
    dots = esper.get_components(Position, Dot)

    for ent_id, (dot_pos, _dot_tag) in dots:
        # Distance au carré < (Rayon Joueur 10 + Rayon Dot 3)^2
        # = 169. On prend 200 (marge).
        if (player_pos.x - dot_pos.x) ** 2 + (
            player_pos.y - dot_pos.y
        ) ** 2 < 200:
            # MIAM ! On supprime l'entité gomme du monde
            esper.delete_entity(ent_id)
            player_score.value += points_per_pacgum


def check_pellet_collisions(player_pos: Position, player_score: Score) -> None:
    """Gère la consommation des Power Pellets.

    Args:
        player_pos: Position pixel du joueur.
        player_score: Composant Score du joueur (muté en place).
    """
    pellets = esper.get_components(Position, PowerPellet)
    points_per_super_pacgum = config["points_per_super_pacgum"]
    for ent_id, (pellet_pos, _) in pellets:
        # Distance au carré < (Rayon Joueur 10 + Rayon Pellet 8)^2 = 324.
        if (player_pos.x - pellet_pos.x) ** 2 + (
            player_pos.y - pellet_pos.y
        ) ** 2 < 324:
            esper.delete_entity(ent_id)
            player_score.value += points_per_super_pacgum
            # On rend TOUS les fantômes vulnérables
            # pour 600 frames (10 secondes)
            for ghost_ent, _ in esper.get_component(Ghost):
                # Un fantôme en respawn ne peut pas devenir vulnérable
                if esper.has_component(ghost_ent, Respawning):
                    continue
                # Si le fantôme était déjà vulnérable,
                # on écrase le timer (reset)
                # Sinon on ajoute le composant
                esper.add_component(ghost_ent, Vulnerable(timer=600))


def eat_ghost(ent_id: int, player_score: Score, cols: int, rows: int) -> None:
    """Mange un fantôme vulnérable et le met en attente avant réapparition.

    Le fantôme est placé hors écran et reçoit un composant Respawning.
    Il réapparaîtra à son point de spawn après 5 secondes (300 frames).

    Args:
        ent_id: ID de l'entité fantôme mangée.
        player_score: Composant Score du joueur (muté en place).
        cols: Nombre de colonnes du labyrinthe.
        rows: Nombre de lignes du labyrinthe.
    """
    points_per_ghost = config["points_per_ghost"]
    player_score.value += points_per_ghost
    esper.remove_component(ent_id, Vulnerable)

    # Place le fantôme hors écran pendant l'attente
    ghost_pixel_pos = esper.component_for_entity(ent_id, Position)
    ghost_pixel_pos.x, ghost_pixel_pos.y = -100, -100

    # Ajoute le timer de réapparition (5 secondes = 300 frames à 60 FPS)
    esper.add_component(ent_id, Respawning(timer=300))


def lose_life(
    player_ent: int, player_gpos: GridPosition,
    player_pos: Position, cols: int, rows: int,
) -> None:
    """Gère la perte d'une vie lors d'un contact avec un fantôme normal.

    Args:
        player_ent: ID de l'entité joueur.
        player_gpos: Position grille du joueur (mutée en place).
        player_pos: Position pixel du joueur (mutée en place).
        cols: Nombre de colonnes du labyrinthe.
        rows: Nombre de lignes du labyrinthe.
    """
    for _ent, live in esper.get_component(Lives):
        live.value -= 1
        if live.value == 0:
            esper.create_entity(GameOver())
        else:
            # Reset joueur au centre
            player_gpos.row, player_gpos.col = 7, 7
            player_pos.x, player_pos.y = grid_to_pixel(7, 7, cols, rows)

            # Invincibilité temporaire (120 frames = ~2 secondes)
            esper.add_component(player_ent, Invincible(timer=120))


def check_ghost_collisions(
    player_ent: int, player_gpos: GridPosition,
    player_pos: Position, player_score: Score,
    cols: int, rows: int,
) -> None:
    """Gère les collisions avec les fantômes (Manger ou Mourir).

    Args:
        player_ent: ID de l'entité joueur.
        player_gpos: Position grille du joueur.
        player_pos: Position pixel du joueur.
        player_score: Composant Score du joueur.
        cols: Nombre de colonnes du labyrinthe.
        rows: Nombre de lignes du labyrinthe.
    """
    # Si le joueur est invincible, on skip
    if esper.has_component(player_ent, Invincible):
        return

    ghosts = esper.get_components(Position, Ghost)
    for ent_id, (ghost_pos, _ghost) in ghosts:
        # Un fantôme en cours de réapparition ne peut pas toucher le joueur
        if esper.has_component(ent_id, Respawning):
            continue

        # "Est-ce que la distance entre Pac-Man et le Fantôme
        # est assez petite pour qu'ils se touchent ?"
        if (player_pos.x - ghost_pos.x) ** 2 + (
            player_pos.y - ghost_pos.y
        ) ** 2 < 300:
            if esper.has_component(ent_id, Vulnerable):
                eat_ghost(ent_id, player_score, cols, rows)
            else:
                lose_life(player_ent, player_gpos, player_pos, cols, rows)
                return


class CollisionProcessor(esper.Processor):
    """
    Gère les interactions entre entités
    (Manger des points, toucher un fantôme).
    """

    def process(self, cols: int, rows: int, **kwargs: Any) -> None:
        """Vérifie les collisions et gère les timers
        d'invincibilité et de niveau.

        Args:
            cols: Nombre de colonnes du labyrinthe.
            rows: Nombre de lignes du labyrinthe.
            **kwargs: Arguments supplémentaires ignorés.
        """
        # 1. On récupère la position du Joueur
        info = get_player_info()

        if info is None:
            return
        player_ent, player_gpos, player_pos, player_score = info

        # 2. Décrémenter le timer d'invincibilité
        if esper.has_component(player_ent, Invincible):
            inv = esper.component_for_entity(player_ent, Invincible)
            inv.timer -= 1
            if inv.timer <= 0:
                esper.remove_component(player_ent, Invincible)

        # 3. Décrémenter le timer du niveau (compte à rebours)
        timer = esper.component_for_entity(player_ent, Timer)
        timer.frames -= 1
        if timer.frames <= 0:
            esper.create_entity(TimeUp())
            return

        # 4. On vérifie les collisions
        check_dot_collisions(player_pos, player_score)
        check_pellet_collisions(player_pos, player_score)
        check_ghost_collisions(
            player_ent, player_gpos, player_pos, player_score, cols, rows
        )
