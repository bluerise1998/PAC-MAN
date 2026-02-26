from __future__ import annotations

import random
from typing import Any

import esper

from ecs.components import (
    Ghost, GridPosition, Player,
    Position, Respawning, Vulnerable,
)
from utils import (
    get_bfs_direction,
    get_valid_directions,
    grid_to_pixel,
    try_move_entity,
)


def get_player_grid_position() -> GridPosition | None:
    """Recherche la position du joueur sur la grille.

    Returns:
        GridPosition | None: La GridPosition du joueur,
            ou None s'il n'existe pas.
    """
    components = esper.get_components(GridPosition, Player)
    for _ent, (gpos, _player) in components:
        return gpos
    return None


def update_vulnerability_timers() -> None:
    """Décrémente les timers de vulnérabilité
    et retire le composant quand expiré."""
    for ent_id, vuln in esper.get_component(Vulnerable):
        vuln.timer -= 1
        if vuln.timer <= 0:
            # Le temps est écoulé, le fantôme redevient normal
            esper.remove_component(ent_id, Vulnerable)


def update_respawn_timers(cols: int, rows: int) -> None:
    """Décrémente les timers de réapparition des fantômes mangés.
    Quand le timer expire, le fantôme réapparaît à son point de spawn."""
    for ent_id, resp in esper.get_component(Respawning):
        resp.timer -= 1
        if resp.timer <= 0:
            esper.remove_component(ent_id, Respawning)
            # Téléporte le fantôme à son point de spawn
            ghost = esper.component_for_entity(ent_id, Ghost)
            ghost_grid_pos = esper.component_for_entity(
                ent_id, GridPosition,
            )
            ghost_pixel_pos = esper.component_for_entity(
                ent_id, Position,
            )
            ghost_grid_pos.row = ghost.spawn_row
            ghost_grid_pos.col = ghost.spawn_col
            ghost_pixel_pos.x, ghost_pixel_pos.y = grid_to_pixel(
                ghost.spawn_row, ghost.spawn_col, cols, rows
            )


def get_ghost_positions(ghost_comps: Any) -> dict[int, tuple[int, int]]:
    """Liste les positions actuelles de tous les fantômes
    pour l'anti-superposition.

    Args:
        ghost_comps: Résultat de esper.get_components pour les fantômes.

    Returns:
        dict[int, tuple[int, int]]: Dictionnaire {ent_id: (row, col)}.
    """
    ghost_positions = {}
    for ent_id, (gpos, _, _) in ghost_comps:
        ghost_positions[ent_id] = (gpos.row, gpos.col)
    return ghost_positions


def compute_target(
    ent_id: int, player_gpos: GridPosition,
    cols: int, rows: int,
) -> GridPosition:
    """Calcule la case cible virtuelle du fantôme selon sa stratégie.

    Args:
        ent_id: ID de l'entité fantôme.
        player_gpos: Position grille du joueur.
        cols: Nombre de colonnes du labyrinthe.
        rows: Nombre de lignes du labyrinthe.

    Returns:
        GridPosition: La case cible virtuelle.
    """
    # 1. Si le fantôme est VULNÉRABLE, il fuit !
    if esper.has_component(ent_id, Vulnerable):
        # On cherche le coin le plus éloigné du joueur pour fuir
        corners = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]

        # On prend le coin qui a la plus grande distance
        # au carré avec le joueur.
        # On utilise Pythagore (a^2 + b^2) pour comparer
        # les distances sans faire de racine carrée
        # (plus rapide).
        # c[0] = ligne (Y), c[1] = colonne (X).
        best_corner = max(
            corners,
            key=lambda c: (
                (c[0] - player_gpos.row) ** 2 + (c[1] - player_gpos.col) ** 2
            ),
        )
        return GridPosition(best_corner[0], best_corner[1])

    # 2. Sinon, il chasse le joueur (Stratégie normale)
    # Pour éviter que les fantômes se suivent à la queue leu leu,
    # on décale leur cible en fonction de leur ID.
    offset_r, offset_c = 0, 0

    # Distribution des rôles : on utilise le modulo (%)
    # pour avoir 0, 1, 2 ou 3.
    # Cela permet de cycler entre les stratégies
    # peu importe le nombre de fantômes.
    strategy = ent_id % 4

    if strategy == 1:
        offset_c = (
            4  # Stratégie 1 : Vise 4 cases à DROITE (Interception horizontale)
        )
    elif strategy == 2:
        offset_r = (
            4  # Stratégie 2 : Vise 4 cases en BAS (Interception verticale)
        )
    elif strategy == 3:
        offset_r, offset_c = (
            -4,
            -4,
        )  # Stratégie 3 : Vise en diagonale HAUT-GAUCHE (Prise en tenaille)
    # Stratégie 0 (par défaut) : Vise directement le joueur (offset 0,0)

    # On calcule la case cible virtuelle (en restant dans les limites du jeu)
    # On utilise max() et min() pour s'assurer que
    # la cible ne sort pas de la grille.
    target_r = max(0, min(rows - 1, player_gpos.row + offset_r))
    target_c = max(0, min(cols - 1, player_gpos.col + offset_c))
    return GridPosition(target_r, target_c)


def choose_direction(
    gpos: GridPosition,
    virtual_target: GridPosition,
    maze: list[list[int]],
    cols: int, rows: int,
) -> str | None:
    """Choisit la direction du fantôme (BFS 80% / aléatoire 20%).

    Args:
        gpos: Position grille actuelle du fantôme.
        virtual_target: Case cible virtuelle.
        maze: La grille du labyrinthe (liste 2D d'entiers bitmask).
        cols: Nombre de colonnes du labyrinthe.
        rows: Nombre de lignes du labyrinthe.

    Returns:
        str | None: La direction choisie ou None.
    """
    best_dir = None
    if random.random() < 0.7:
        best_dir = get_bfs_direction(gpos, virtual_target, maze, cols, rows)

    # Si l'IA a "glissé" (les 20%) ou si le BFS n'a pas trouvé de chemin
    if not best_dir:
        valid_dirs = get_valid_directions(gpos, maze)
        if valid_dirs:
            best_dir = random.choice(valid_dirs)

    return best_dir


def try_ghost_move(
    ent_id: int, gpos: GridPosition,
    best_dir: str, maze: list[list[int]],
    ghost_positions: dict[int, tuple[int, int]],
) -> None:
    """Tente de déplacer un fantôme en vérifiant l'anti-superposition.

    Args:
        ent_id: ID de l'entité fantôme.
        gpos: Position grille du fantôme (mutée en place).
        best_dir: Direction choisie ("UP", "DOWN", "LEFT", "RIGHT").
        maze: La grille du labyrinthe (liste 2D d'entiers bitmask).
        ghost_positions: Positions de tous les fantômes (muté en place).
    """
    next_r, next_c = gpos.row, gpos.col
    if best_dir == "UP":
        next_r -= 1
    elif best_dir == "DOWN":
        next_r += 1
    elif best_dir == "LEFT":
        next_c -= 1
    elif best_dir == "RIGHT":
        next_c += 1

    # On vérifie si cette case est déjà occupée par un autre fantôme.
    # On parcourt la liste de tous les fantômes pour
    # voir si l'un d'eux est déjà sur la case cible.
    is_occupied = False
    for other_id, other_pos in ghost_positions.items():
        # On ne se compare pas à soi-même (other_id != ent_id).
        # Si un autre fantôme est sur la case où on
        # veut aller, c'est un embouteillage !
        if other_id != ent_id and other_pos == (next_r, next_c):
            is_occupied = True
            break

    # Si la voie est libre (pas de copain fantôme
    # sur la case), on tente le mouvement physique.
    if not is_occupied:
        # try_move_entity vérifie les murs du labyrinthe.
        if try_move_entity(gpos, best_dir, maze):
            # Si le mouvement a réussi, on met à jour
            # notre position dans le dictionnaire.
            # C'est CRUCIAL : cela permet aux fantômes
            # suivants (dans la même boucle)
            # de savoir que cette case est maintenant prise par nous.
            ghost_positions[ent_id] = (gpos.row, gpos.col)


class GhostAIProcessor(esper.Processor):
    """Système d'IA pour les fantômes.

    Calcule le chemin vers le joueur à chaque intersection.
    """

    def process(
        self, maze: list[list[int]],
        cols: int, rows: int, **kwargs: Any,
    ) -> None:
        """Met à jour la direction des fantômes pour chasser le joueur.

        Args:
            maze: La grille du labyrinthe (liste 2D d'entiers bitmask).
            cols: Nombre de colonnes du labyrinthe.
            rows: Nombre de lignes du labyrinthe.
            **kwargs: Arguments supplémentaires ignorés.
        """
        # 1. RÉCUPÉRATION DU JOUEUR
        # On a besoin de sa position pour que les fantômes sachent qui chasser.
        player_gpos = get_player_grid_position()

        if not player_gpos:
            # SÉCURITÉ : Si le joueur n'existe pas
            # (ex: supprimé après un Game Over),
            # on arrête l'IA tout de suite pour éviter un crash plus bas.
            return

        # 2. GESTION DES TIMERS (VULNÉRABILITÉ + RÉAPPARITION)
        # On met à jour le temps restant pour les fantômes bleus.
        # Si le temps est écoulé, ils redeviennent normaux.
        update_vulnerability_timers()
        # On met à jour les timers de réapparition des fantômes mangés.
        update_respawn_timers(cols, rows)

        # 3. RÉCUPÉRATION DES FANTÔMES
        # On récupère tous les fantômes pour gérer leur déplacement.
        ghost_comps = esper.get_components(
            GridPosition,
            Position,
            Ghost,
        )

        # 4. PRÉPARATION ANTI-COLLISION
        # On crée une carte des positions actuelles de tous les fantômes
        # pour éviter qu'ils ne se rentrent dedans.
        ghost_positions = get_ghost_positions(ghost_comps)

        # 5. BOUCLE PRINCIPALE DE L'IA
        for ent_id, (gpos, pos, _ghost) in ghost_comps:
            # Skip les fantômes en attente de réapparition
            if esper.has_component(ent_id, Respawning):
                continue

            # A. VERROUILLAGE (Grid Locking)
            # On vérifie si le fantôme est physiquement
            # arrivé au centre de sa case.
            # Tant qu'il est en mouvement (glissement),
            # on ne change pas d'avis.
            target_x, target_y = grid_to_pixel(gpos.row, gpos.col, cols, rows)
            if pos.x != target_x or pos.y != target_y:
                continue

            # B. CHOIX DE LA CIBLE (Stratégie)
            # Selon l'ID du fantôme et son état (Vulnérable ou non),
            # on détermine quelle case il doit viser
            # (Joueur, Coin, Intersection...).
            virtual_target = compute_target(ent_id, player_gpos, cols, rows)

            # C. CALCUL DE LA DIRECTION (Pathfinding)
            # On utilise le BFS (80% du temps) ou le hasard (20%) pour choisir
            # la meilleure direction vers la cible virtuelle.
            best_dir = choose_direction(gpos, virtual_target, maze, cols, rows)

            # D. DÉPLACEMENT
            # Si une direction est choisie, on tente de bouger en vérifiant
            # qu'on ne fonce pas dans un mur ni dans un autre fantôme.
            if best_dir:
                try_ghost_move(ent_id, gpos, best_dir, maze, ghost_positions)
