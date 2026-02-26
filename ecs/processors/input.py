from typing import Any

import esper
import pygame

from ecs.components import GridPosition, Player, Position
from utils import grid_to_pixel, try_move_entity


class InputProcessor(esper.Processor):
    """
    Système de gestion des Entrées (Clavier).
    Responsable de lire les touches pressées et de diriger le Joueur.
    """

    def process(
        self, maze: list[list[int]],
        cols: int, rows: int, **kwargs: Any,
    ) -> None:
        """Vérifie les entrées clavier et met à jour la GridPosition du joueur.

        Args:
            maze: La grille du labyrinthe (liste 2D d'entiers bitmask).
            cols: Nombre de colonnes du labyrinthe.
            rows: Nombre de lignes du labyrinthe.
            **kwargs: Arguments supplémentaires ignorés.
        """
        # pygame.key.get_pressed() retourne une Séquence (tuple de booléens),
        # pas un dict. On accède à l'état d'une touche via son index entier
        # (ex: keys[pygame.K_UP] revient à lire la case n°273 du tableau).
        keys = pygame.key.get_pressed()

        # On récupère les entités qui ont une position (Grille + Pixels)
        # ET le tag 'Player'.
        # C'est ici que tu dis : "Je veux OBLIGATOIREMENT le composant Player"
        components = esper.get_components(GridPosition, Position, Player)
        # _ent     : reçoit l'ID (1) -> Le tiret bas _ signifie "on s'en fiche"
        # gpos     : reçoit l'objet GridPosition(7,7)
        # pos      : reçoit l'objet Position(350,300)
        # _player  : reçoit l'objet Player() ->
        # on s'en fiche, il servait juste de filtre
        for _ent, (gpos, pos, _player) in components:
            # 1. Calcul de la position cible en pixels (le centre de la case)
            #    basé sur la position logique actuelle (GridPosition).
            target_x, target_y = grid_to_pixel(gpos.row, gpos.col, cols, rows)

            # 2. VERROUILLAGE DU MOUVEMENT (Grid Locking) :
            #    On compare la position visuelle (pos) avec la cible (target).
            #
            #    Si pos.x != target_x, cela signifie que le sprite est encore
            #    en train de glisser vers sa case.
            #
            #    On utilise 'continue' pour empêcher tout changement de
            #    direction tant que le personnage n'est pas parfaitement
            #    centré sur sa case. Cela garantit un déplacement strict
            #    "case par case" sans pouvoir tourner au milieu d'un mur.
            if pos.x != target_x or pos.y != target_y:
                continue

            # 3. Si on est à l'arrêt (centré), on écoute le clavier.
            #    try_move_entity va vérifier s'il y a un mur dans la direction
            #    souhaitée et mettre à jour gpos si la voie est libre.
            if keys[pygame.K_UP]:
                try_move_entity(gpos, "UP", maze)
            elif keys[pygame.K_RIGHT]:
                try_move_entity(gpos, "RIGHT", maze)
            elif keys[pygame.K_DOWN]:
                try_move_entity(gpos, "DOWN", maze)
            elif keys[pygame.K_LEFT]:
                try_move_entity(gpos, "LEFT", maze)
