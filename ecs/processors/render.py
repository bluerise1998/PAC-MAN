from typing import Any

import esper
import pygame

from ecs.components import (
    Level, Lives, Player, Position,
    Respawning, Score, Sprite, Timer, Vulnerable,
)
from maze.constants import WINDOW_W
from utils import resource_path

# Cache des images chargées : évite de recharger le PNG à chaque frame
_image_cache = {}


def _get_image(path: str, size: int) -> pygame.Surface:
    """Charge une image depuis le cache, ou la charge et la redimensionne.

    Args:
        path: Chemin vers le fichier image PNG.
        size: Taille cible en pixels (largeur et hauteur).

    Returns:
        pygame.Surface: L'image redimensionnée.
    """
    # 1. Création d'une clé unique (Signature)
    # pour identifier cette version de l'image
    key = (path, size)

    # 2. Vérification dans le dictionnaire (Le Cache) :
    # "Est-ce que j'ai déjà fait ce travail ?"
    if key not in _image_cache:
        # 3. Le travail lourd (exécuté UNE SEULE FOIS par taille/image)
        # a. Chargement depuis le disque (Lent) + Optimisation transparence
        img = pygame.image.load(resource_path(path)).convert_alpha()
        # b. Redimensionnement mathématique (Coûteux) et Stockage en mémoire
        _image_cache[key] = pygame.transform.scale(img, (size, size))

    # 4. Retour immédiat de l'image prête (Rapide)
    return _image_cache[key]


def draw_sprites(surface: pygame.Surface) -> None:
    """Dessine toutes les entités graphiques à leur position écran.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
    """
    components = esper.get_components(Position, Sprite)

    for ent_id, (pos, sprite) in components:
        # Ne pas dessiner les fantômes en attente de réapparition
        if esper.has_component(ent_id, Respawning):
            continue

        # Si le sprite a une image PNG, on l'affiche
        if sprite.image:
            # 1. Calcul de la taille réelle (Diamètre)
            # Le rayon (radius) c'est la moitié (du centre au bord).
            # L'image est un carré complet, donc il faut le double (diamètre).
            size = sprite.radius * 2

            # 2. Gestion du mode "Vulnérable" (Fantômes bleus)
            image_path = sprite.image
            if esper.has_component(ent_id, Vulnerable):
                image_path = "assets/weak.png"

            # 3. Récupération et Affichage
            img = _get_image(image_path, size)
            rect = img.get_rect(center=(int(pos.x), int(pos.y)))
            surface.blit(img, rect)
        else:
            # Pas d'image → cercle coloré (dots, power pellets)
            pygame.draw.circle(
                surface, sprite.color, (int(pos.x), int(pos.y)), sprite.radius
            )


def draw_score(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Affiche le score du joueur en haut à gauche.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        font: La police à utiliser pour le rendu du texte.
    """
    # On récupère le score du joueur (il n'y en a qu'un)
    # 'score_comp' est l'OBJET Score (le conteneur).
    # Pour avoir le nombre, on doit demander 'score_comp.value'.
    for _ent, (score_comp, _player) in esper.get_components(Score, Player):
        score_text = font.render(
            f"Score: {score_comp.value}", True, (255, 255, 255)
        )
        surface.blit(score_text, (10, 10))


def draw_level(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Affiche le niveau actuel du joueur.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        font: La police à utiliser pour le rendu du texte.
    """
    for ent, (_score, _player) in esper.get_components(Score, Player):
        level_comp = esper.component_for_entity(ent, Level)
        level_text = font.render(
            f"Level: {level_comp.value}/10", True, (255, 255, 255)
        )
        rect = level_text.get_rect(midtop=(WINDOW_W // 4, 10))
        surface.blit(level_text, rect)


def draw_lives(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Affiche les vies du joueur au centre.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        font: La police à utiliser pour le rendu du texte.
    """
    for ent, (_score, _player) in esper.get_components(Score, Player):
        lives_comp = esper.component_for_entity(ent, Lives)
        lives_text = font.render(
            f"Life: {lives_comp.value}", True, (255, 255, 255)
        )
        rect = lives_text.get_rect(
            midtop=(7 * WINDOW_W // 16, 10)
        )
        surface.blit(lives_text, rect)


def draw_timer(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Affiche le temps restant à côté des vies.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        font: La police à utiliser pour le rendu du texte.
    """
    for ent, (_score, _player) in esper.get_components(Score, Player):
        timer = esper.component_for_entity(ent, Timer)
        seconds = timer.frames // 60
        timer_text = font.render(f"Time: {seconds}s", True, (255, 255, 255))
        rect = timer_text.get_rect(
            midtop=(5 * WINDOW_W // 8, 10)
        )
        surface.blit(timer_text, rect)


def draw_highscore(
    surface: pygame.Surface,
    font: pygame.font.Font, highscore: int,
) -> None:
    """Affiche le meilleur score en haut à droite.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        font: La police à utiliser pour le rendu du texte.
        highscore: Le meilleur score à afficher.
    """
    hs_text = font.render(f"Highscore: {highscore}", True, (255, 255, 255))
    surface.blit(hs_text, (WINDOW_W - hs_text.get_width() - 10, 10))


class RenderProcessor(esper.Processor):
    """
    Système de Rendu.
    Dessine toutes les entités graphiques (Sprites) à leur Position écran.
    """

    def process(
        self, surface: pygame.Surface,
        highscore: int = 0, **kwargs: Any,
    ) -> None:
        """Dessine tous les sprites et l'interface
        (score, vies, timer, highscore).

        Args:
            surface: La surface Pygame sur laquelle dessiner.
            highscore: Le meilleur score à afficher.
            **kwargs: Arguments supplémentaires ignorés.
        """
        # On charge la police locale (sans self)
        font = pygame.font.Font(None, 30)

        draw_sprites(surface)
        draw_score(surface, font)
        draw_level(surface, font)
        draw_lives(surface, font)
        draw_timer(surface, font)
        draw_highscore(surface, font, highscore)
