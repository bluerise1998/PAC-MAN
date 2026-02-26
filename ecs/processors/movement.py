from typing import Any

import esper

from ecs.components import GridPosition, Position
from utils import grid_to_pixel

MOVE_SPEED = 3


class MovementProcessor(esper.Processor):
    """
    Système de Mouvement et d'Animation.
    Gère l'interpolation fluide entre la position actuelle et la destination.
    """

    def process(self, cols: int, rows: int, **kwargs: Any) -> None:
        """Déplace les sprites pixel par pixel vers leur GridPosition.

        Args:
            cols: Nombre de colonnes du labyrinthe.
            rows: Nombre de lignes du labyrinthe.
            **kwargs: Arguments supplémentaires ignorés.
        """
        # On prend toutes les entités qui ont une position logique et visuelle.
        components = esper.get_components(GridPosition, Position)

        for _ent, (gpos, pos) in components:
            # Où l'entité devrait-elle être idéalement ?
            target_x, target_y = grid_to_pixel(gpos.row, gpos.col, cols, rows)

            # Calcul de la distance restante (Delta)
            dx = target_x - pos.x
            dy = target_y - pos.y

            # INTERPOLATION : C'est ici qu'on déplace
            # le visuel "étape par étape".
            # La GridPosition a déjà changé instantanément
            # (téléportation logique),
            # mais la Position (pixels) doit rattraper ce
            # retard petit à petit (MOVE_SPEED)
            # pour créer l'illusion du mouvement fluide.
            # --- Gestion de l'axe X ---
            if abs(dx) < MOVE_SPEED:
                # Si on est très proche (moins d'un pas), on "snap" directement
                # à la position finale pour éviter de dépasser et vibrer.
                pos.x = target_x
            elif dx > 0:
                # La cible est à droite -> on avance
                pos.x += MOVE_SPEED
            else:
                # La cible est à gauche -> on recule
                pos.x -= MOVE_SPEED

            # --- Gestion de l'axe Y ---
            if abs(dy) < MOVE_SPEED:
                pos.y = target_y
            elif dy > 0:
                pos.y += MOVE_SPEED
            else:
                pos.y -= MOVE_SPEED
