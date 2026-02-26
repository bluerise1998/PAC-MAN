"""Génération du labyrinthe."""

from mazegenerator import MazeGenerator


def generate_maze(seed: int = 0) -> tuple[list[list[int]], int, int]:
    """Génère un labyrinthe 15x15 et retourne (maze, cols, rows).

    Args:
        seed: Seed pour la génération du labyrinthe.
    """
    cols = 15
    rows = 15
    generator = MazeGenerator(size=(cols, rows), seed=seed)
    return generator.maze, cols, rows
