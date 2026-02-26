"""Composants ECS — chaque composant est juste un conteneur de données."""

from dataclasses import dataclass


@dataclass
class GridPosition:
    """Position LOGIQUE sur la grille (ex: ligne 7, colonne 7).
    C'est la 'vraie' position pour le jeu (collisions, murs)."""

    row: int
    col: int


@dataclass
class Position:
    """Position PIXELS sur l'écran (ex: x=350.5, y=300.0).

    Sert uniquement à l'animation fluide.
    Elle court après la Position logique."""

    x: float
    y: float


@dataclass
class Sprite:
    """Composant VISUEL.
    Définit l'apparence de l'entité (Couleur et Taille).
    Si image est fourni, on affiche l'image PNG à la place du cercle."""

    radius: int  # Rayon du cercle en pixels
    color: tuple = (255, 255, 255)  # (R, G, B) ex: (255, 255, 0) pour Jaune
    image: str | None = None  # Chemin vers l'image PNG (optionnel)


@dataclass
class Player:
    """Tag (étiquette) : Seules les entités avec ce tag écoutent le clavier.
    Sert de filtre pour l'InputProcessor."""

    pass


@dataclass
class Ghost:
    """Tag : entités pilotées par l'IA.

    Sert de filtre pour le GhostAIProcessor."""

    spawn_row: int = 0
    spawn_col: int = 0


@dataclass
class Dot:
    """Tag : Les petites gommes à manger pour le score.
    Sert de filtre pour le CollisionProcessor."""

    pass


@dataclass
class PowerPellet:
    """Tag : Les grosses boules qui rendent les fantômes vulnérables."""

    pass


@dataclass
class Vulnerable:
    """Composant temporaire ajouté aux fantômes
    quand Pac-Man mange une PowerPellet.
    timer (int) : Nombre de frames avant que le
    fantôme redevienne normal.
    """

    timer: int


@dataclass
class Respawning:
    """Composant temporaire ajouté aux fantômes mangés.
    Le fantôme est invisible et inactif pendant le timer.
    timer (int) : Nombre de frames avant réapparition (5s = 300 frames)."""

    timer: int


@dataclass
class Score:
    """Stocke le score actuel du joueur."""

    value: int


@dataclass
class Lives:
    """Stocke le nombre de vies restantes du joueur."""

    value: int


@dataclass
class Invincible:
    """Composant temporaire ajouté au joueur après avoir perdu une vie.
    timer (int) : Nombre de frames d'invincibilité restantes."""

    timer: int


@dataclass
class Timer:
    """Compte à rebours du niveau en frames (ex: 90s * 60fps = 5400 frames)."""

    frames: int


@dataclass
class Level:
    """Niveau actuel du joueur (1 à 10)."""

    value: int


@dataclass
class GameOver:
    """Tag pour signaler la fin de partie."""

    pass


@dataclass
class TimeUp:
    """Tag pour signaler que le temps du niveau est écoulé."""

    pass
