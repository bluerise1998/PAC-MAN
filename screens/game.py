"""Écran de jeu — affiche le labyrinthe."""

from __future__ import annotations

import random

import esper
import pygame

from ecs.components import (
    Dot,
    GameOver,
    Ghost,
    GridPosition,
    Invincible,
    Level,
    Lives,
    Player,
    Position,
    PowerPellet,
    Score,
    Sprite,
    TimeUp,
    Timer,
)
import ecs.processors.movement as movement_mod
from ecs.processors import (
    CollisionProcessor,
    GhostAIProcessor,
    InputProcessor,
    MovementProcessor,
    RenderProcessor,
)
from maze.generation import generate_maze
from maze.rendering import draw_maze
from parser.parser import config
from screens.game_over import run_game_over, run_winner
from screens.highscores import get_best_score, save_highscore
from utils import grid_to_pixel


def create_player(
    cols: int, rows: int, score: int = 0,
    level: int = 1, lives: int | None = None,
) -> None:
    """
    Crée l'entité du joueur (Pac-Man) au centre du labyrinthe.

    Args:
        cols (int): Nombre total de colonnes.
        rows (int): Nombre total de lignes.
        score (int): Score à conserver (pour le passage de niveau).
        level (int): Niveau actuel (1 à 10).
        lives (int | None): Vies restantes (None = valeur config).
    """
    # 1. Conversion de la position grille (7, 7) en pixels (x, y)
    #    pour que le sprite s'affiche au bon endroit dès le début.
    x, y = grid_to_pixel(7, 7, cols, rows)

    if lives is None:
        lives = config["lives"]

    # 2. Création de l'entité dans le monde ECS avec ses composants
    esper.create_entity(
        GridPosition(7, 7),  # Case (7, 7)
        Position(x, y),  # Pixels (x, y)
        Sprite(10, image="assets/pacman.png"),
        Player(),  # Tag Joueur
        Score(score),  # Score conservé entre les niveaux
        Lives(lives),
        Timer(config["level_max_time"] * 60),  # 90s * 60fps = 5400 frames
        Level(level),
    )


def create_ghosts(cols: int, rows: int) -> None:
    """Crée 4 entités 'Fantôme' positionnées aux coins du labyrinthe.

    Args:
        cols: Nombre total de colonnes du labyrinthe.
        rows: Nombre total de lignes du labyrinthe.
    """
    ghost_data = [
        (0, 0, "assets/red.png"),
        (0, 14, "assets/blue.png"),
        (14, 0, "assets/yellow.png"),
        (14, 14, "assets/green.png"),
    ]

    for r, c, img in ghost_data:
        x, y = grid_to_pixel(r, c, cols, rows)
        esper.create_entity(
            GridPosition(r, c), Position(x, y),
            Sprite(10, image=img), Ghost(spawn_row=r, spawn_col=c)
        )


def create_power_pellets(cols: int, rows: int) -> list[tuple[int, int]]:
    """Crée 4 grosses boules (Power Pellets) près des coins.

    Args:
        cols: Nombre total de colonnes du labyrinthe.
        rows: Nombre total de lignes du labyrinthe.

    Returns:
        list[tuple[int, int]]: Positions des pellets pour exclure des dots.
    """
    # Coordonnées approximatives des coins (1,1), (1,13), (13,1), (13,13)
    corners = [(1, 1), (1, rows - 2), (cols - 2, 1), (cols - 2, rows - 2)]
    for r, c in corners:
        x, y = grid_to_pixel(r, c, cols, rows)
        esper.create_entity(
            GridPosition(r, c),
            Position(x, y),
            Sprite(8, (255, 182, 193)),  # Rose, rayon plus gros (8)
            PowerPellet(),
        )
    return corners  # On retourne la liste pour que create_dots évite ces cases


def create_dots(
    maze: list[list[int]], cols: int, rows: int,
    forbidden_pos: list[tuple[int, int]],
) -> None:
    """Remplit le labyrinthe de petites gommes (Dots).

    Args:
        maze: La grille du labyrinthe (liste 2D d'entiers bitmask).
        cols: Nombre total de colonnes du labyrinthe.
        rows: Nombre total de lignes du labyrinthe.
        forbidden_pos: Positions à exclure (power pellets, etc.).
    """
    for r in range(rows):
        for c in range(cols):
            # On ne met pas de gomme sur la case de départ du joueur (7, 7)
            if r == 7 and c == 7:
                continue

            # On ne met pas de gomme dans les murs pleins
            # (valeur 15), comme le "42".
            if maze[r][c] == 15:
                continue

            # On ne met pas de gomme là où il y a déjà une Power Pellet
            if (r, c) in forbidden_pos:
                continue

            # Calcul de la position pixel
            x, y = grid_to_pixel(r, c, cols, rows)

            # Création de l'entité Gomme
            esper.create_entity(
                GridPosition(r, c),
                Position(x, y),
                Sprite(3, (255, 182, 193)),  # Rose clair, petit rayon (3)
                Dot(),
            )


def handle_input(events: list[pygame.event.Event]) -> str | None:
    """Gère les événements globaux (fermeture fenêtre, touche Echap).

    Args:
        events: Liste des événements Pygame de la frame.

    Returns:
        str | None: Le nom du prochain écran si changement, sinon None.
    """
    for event in events:
        if event.type == pygame.QUIT:
            return "Exit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            if event.key == pygame.K_SPACE:
                return "pause"
            if event.key == pygame.K_n:
                return "next_level"
            if event.key == pygame.K_c:
                return "cheat"
    return None


def _get_current_progress() -> tuple[int, int]:
    """Récupère le score et le niveau actuels du joueur.

    Returns:
        tuple[int, int]: (score, level) ou (0, 1) par défaut.
    """
    for _ent, (score_comp, _player, level_comp) in esper.get_components(
        Score, Player, Level,
    ):
        return score_comp.value, level_comp.value
    return 0, 1


def _skip_to_next_level(
    surface: pygame.Surface,
    level_seeds: list[int],
) -> tuple[
    str | None, list[list[int]] | None,
    int | None, int | None,
]:
    """DEBUG : Passe au niveau suivant (touche N).

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        level_seeds: Liste des seeds pour chaque niveau.

    Returns:
        tuple: (page, maze, cols, rows)
        ou (page, None, None, None) si victoire.
    """
    current_score, current_level = _get_current_progress()
    _cleanup_ecs()
    if current_level >= 10:
        page, pseudo = run_winner(surface, current_score)
        save_highscore(pseudo if pseudo else "???", current_score)
        return page, None, None, None
    next_level = current_level + 1
    maze, cols, rows = _init_level(
        current_score, next_level, level_seeds[next_level],
    )
    return None, maze, cols, rows


_BASE_MOVE_SPEED = movement_mod.MOVE_SPEED


def _toggle_cheat(active: bool) -> None:
    """CHEAT : Active/désactive la vitesse bonus et l'invincibilité.

    Args:
        active: True pour activer le cheat, False pour désactiver.
    """
    if active:
        movement_mod.MOVE_SPEED = _BASE_MOVE_SPEED + 5
        _apply_cheat_invincibility()
    else:
        movement_mod.MOVE_SPEED = _BASE_MOVE_SPEED
        for ent, _player in esper.get_component(Player):
            if esper.has_component(ent, Invincible):
                esper.remove_component(ent, Invincible)


def _apply_cheat_invincibility() -> None:
    """Applique l'invincibilité cheat au joueur actuel."""
    for ent, _player in esper.get_component(Player):
        esper.add_component(ent, Invincible(timer=999999))


def _draw_pause(surface: pygame.Surface) -> None:
    """Affiche le texte PAUSED en jaune au centre de l'écran.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
    """
    font = pygame.font.Font(None, 80)
    pause_text = font.render("PAUSED", True, (255, 255, 0))
    surface.blit(pause_text, pause_text.get_rect(center=(400, 300)))
    pygame.display.flip()


def _draw_times_up(
    surface: pygame.Surface, selected: int,
) -> None:
    """Affiche TIME'S UP! avec les options Retry / Done.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        selected: Index de l'option sélectionnée (0=Retry, 1=Done).
    """
    surface.fill((0, 0, 0))

    font_big = pygame.font.Font(None, 80)
    font_opt = pygame.font.Font(None, 50)

    title = font_big.render("TIME'S UP!", True, (255, 255, 0))
    surface.blit(title, title.get_rect(center=(400, 250)))

    labels = ["Retry", "Done"]
    for i, label in enumerate(labels):
        color = (255, 255, 0) if i == selected else (255, 255, 255)
        txt = font_opt.render(label, True, color)
        surface.blit(txt, txt.get_rect(center=(400, 330 + i * 70)))

    pygame.display.flip()


def _handle_times_up(surface: pygame.Surface) -> str:
    """Boucle d'attente pour l'écran TIME'S UP.

    Returns:
        str: "retry" ou "done" selon le choix du joueur.
    """
    selected = 0
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "done"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    selected = 1 - selected
                if event.key == pygame.K_RETURN:
                    return "retry" if selected == 0 else "done"

        _draw_times_up(surface, selected)


def _init_level(
    score: int = 0, level: int = 1,
    seed: int = 0, lives: int | None = None,
) -> tuple[list[list[int]], int, int]:
    """Initialise un niveau complet : génère le labyrinthe,
       crée les entités et enregistre les systèmes.

    Args:
        score: Score à conserver depuis le niveau précédent.
        level: Numéro du niveau à initialiser (1 à 10).
        seed: Seed pour la génération du labyrinthe.
        lives: Vies restantes (None = valeur config).

    Returns:
        tuple[list[list[int]], int, int]: (maze, cols, rows).
    """
    # 1. GÉNÉRATION DU NIVEAU :
    #    On récupère la matrice 'maze' (les murs) et les dimensions.
    #    C'est le "terrain de jeu" logique.
    maze, cols, rows = generate_maze(seed)

    # 2. CRÉATION DES ENTITÉS (Le Casting) :
    #    On place le Joueur (Pac-Man) au centre.
    create_player(cols, rows, score, level, lives)
    #    On place les 4 Fantômes aux coins de la carte.
    create_ghosts(cols, rows)
    #    On place les Power Pellets et on récupère leurs positions
    pellet_pos = create_power_pellets(cols, rows)
    #    On sème les gommes partout.
    create_dots(maze, cols, rows, pellet_pos)

    # Enregistrement des Systèmes (Processors) dans le monde ECS.
    # La priorité définit l'ordre d'exécution (plus grand = exécuté avant).
    esper.add_processor(InputProcessor(), priority=3)
    esper.add_processor(GhostAIProcessor(), priority=3)
    esper.add_processor(MovementProcessor(), priority=2)
    esper.add_processor(
        CollisionProcessor(), priority=2
    )  # Juste après le mouvement
    esper.add_processor(RenderProcessor(), priority=1)

    return maze, cols, rows


def _check_game_over() -> int | None:
    """Vérifie si la partie est terminée.

    Returns:
        int | None: Le score final si game over, None sinon.
    """
    if len(esper.get_component(GameOver)) > 0:
        current_score = 0
        for _, (score_comp, _) in esper.get_components(Score, Player):
            current_score = score_comp.value
            break

        _cleanup_ecs()
        return current_score

    return None


def _check_time_up() -> tuple[int, int, int] | None:
    """Vérifie si le temps du niveau est écoulé.

    Returns:
        tuple | None: (score, level, lives) si temps écoulé,
            None sinon.
    """
    if len(esper.get_component(TimeUp)) == 0:
        return None

    for ent, (score_comp, _player, level_comp) in esper.get_components(
        Score, Player, Level,
    ):
        lives_comp = esper.component_for_entity(ent, Lives)
        return score_comp.value, level_comp.value, lives_comp.value

    return None


def _check_level_complete() -> tuple[int, int] | None:
    """Vérifie si toutes les gommes et power pellets ont été mangées.

    Returns:
        tuple | None: (score, level) si niveau terminé, None sinon.
    """
    # S'il reste des gommes ou des power pellets, le niveau n'est pas fini
    dots_left = len(esper.get_component(Dot))
    pellets_left = len(esper.get_component(PowerPellet))
    if dots_left > 0 or pellets_left > 0:
        return None

    # Toutes les gommes mangées ! On récupère le score et le niveau actuels
    for _ent, (score_comp, _player, level_comp) in esper.get_components(
        Score, Player, Level,
    ):
        return score_comp.value, level_comp.value

    return None


def _cleanup_ecs() -> None:
    """Nettoyage du monde ECS : supprime toutes les
    entités et retire les Systèmes."""
    # Nettoyage : on supprime toutes les entités avant de quitter
    # Ce n'est pas du C, c'est juste pour ne pas garder les vieux
    # fantômes et le vieux joueur quand on relancera une partie.
    esper.clear_database()

    # IMPORTANT : On retire aussi les Systèmes (Processors).
    # Sinon, quand on relancera "Start Game", on en ajoutera de nouveaux
    # par-dessus les anciens. Avoir 2 MovementProcessor ferait bouger
    # les entités 2 fois plus vite !
    esper.remove_processor(InputProcessor)
    esper.remove_processor(GhostAIProcessor)
    esper.remove_processor(MovementProcessor)
    esper.remove_processor(CollisionProcessor)
    esper.remove_processor(RenderProcessor)


def run_game(surface: pygame.Surface, page: str) -> str:
    """Fonction principale de l'écran de jeu. Initialise et lance la boucle.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        page: Page courante (doit être "Start Game").

    Returns:
        str: La page suivante ("menu" ou "Exit").
    """
    # 0. GÉNÉRATION DES SEEDS POUR CHAQUE NIVEAU
    #    Niveau 1 : seed fixe depuis config.json (reproductible).
    #    Niveaux 2-10 : seeds aléatoires (différentes à chaque partie).
    level_seeds = [0] + [config["seed"]] + [
        random.randint(1, 2**31 - 1) for _ in range(9)
    ]

    # 1. INITIALISATION DU NIVEAU
    maze, cols, rows = _init_level(seed=level_seeds[1])

    # 2. GESTION DU TEMPS
    clock = pygame.time.Clock()

    # 3. CHARGEMENT DES DONNÉES
    highscore = get_best_score()

    # 4. BOUCLE DE JEU (Game Loop)
    # Cette boucle tourne 60 fois par seconde tant
    # qu'on est sur l'écran "Start Game".
    paused = False
    cheat_active = False

    while page == "Start Game":
        # A. RÉGULATION DE LA VITESSE (Tick)
        # On force le jeu à attendre pour ne pas dépasser 60 images/seconde.
        # Cela garantit que le jeu tourne à la même vitesse sur tous les PC.
        clock.tick(60)

        # B. GESTION DES ÉVÉNEMENTS (Input)
        # On récupère les clics, touches clavier, fermeture de fenêtre...
        events = pygame.event.get()

        # On vérifie si le joueur veut quitter ou changer d'écran (Echap).
        next_page = handle_input(events)
        if next_page == "pause":
            paused = not paused
        elif next_page == "next_level":
            # 1. Appel de la fonction de saut de niveau (Cheat 'N')
            # Elle renvoie soit une nouvelle page (Victoire),
            # soit les données
            # du nouveau niveau.
            (page_result, new_maze,
             new_cols, new_rows) = _skip_to_next_level(
                surface, level_seeds)

            # 2. Gestion de la Victoire
            # Si _skip_to_next_level renvoie une page
            # (ex: "menu" après l'écran de victoire),
            # on quitte la boucle de jeu immédiatement.
            if page_result:
                return page_result

            # 3. Le "Fusible" de sécurité (Fail Fast)
            # Si on n'a pas gagné, on DOIT avoir un nouveau niveau.
            # Si new_maze est None ici, le jeu planterait de toute façon
            # à la frame suivante avec une erreur incompréhensible.
            # L'assert nous donne l'erreur exacte
            # ICI pour faciliter le débogage.
            assert new_maze is not None
            assert new_cols is not None
            assert new_rows is not None

            # 4. Mise à jour du niveau
            # On remplace le labyrinthe actuel par le nouveau pour
            # la frame suivante.
            maze, cols, rows = new_maze, new_cols, new_rows
            if cheat_active:
                _apply_cheat_invincibility()
        elif next_page == "cheat":
            cheat_active = not cheat_active
            _toggle_cheat(cheat_active)
        elif next_page:
            # Si on change d'écran, on nettoie tout (suppression des entités)
            _cleanup_ecs()
            return next_page

        # Si le jeu est en pause, on affiche "PAUSED"
        # par-dessus l'image actuelle
        if paused:
            _draw_pause(surface)
            # C'est ICI que la pause opère !
            # Le mot-clé 'continue' force Python à remonter
            # tout de suite au début du 'while', SANS exécuter
            # le code qui est en dessous (esper.process, etc.).
            # Donc : pas de mouvement, pas d'IA, le jeu est figé.
            continue

        # C. DESSIN DU FOND (Rendering Background)
        # On efface l'écran avec du noir pour repartir sur une base propre.
        surface.fill((0, 0, 0))
        # On dessine les murs du labyrinthe (statique).
        draw_maze(surface, maze, cols, rows)

        # D. MISE À JOUR DU MONDE (ECS Process)
        # C'est le cœur du moteur : on demande à tous
        # les Systèmes de travailler.
        # - InputProcessor : Lit le clavier
        # - GhostAIProcessor : Fait réfléchir les fantômes
        # - MovementProcessor : Déplace les entités
        # - CollisionProcessor : Vérifie les chocs
        # - RenderProcessor : Dessine les sprites et le score
        esper.process(
            maze=maze,
            cols=cols,
            rows=rows,
            surface=surface,
            highscore=highscore,
        )

        # E. VÉRIFICATION DE FIN DE PARTIE
        # On regarde si une entité "GameOver" a été créée
        # par le CollisionProcessor.
        final_score = _check_game_over()
        if final_score is not None:
            page, pseudo = run_game_over(surface, final_score)
            save_highscore(pseudo if pseudo else "???", final_score)
            return page

        # E2. VÉRIFICATION TEMPS ÉCOULÉ (Retry / Done)
        time_up_result = _check_time_up()
        if time_up_result is not None:
            current_score, current_level, current_lives = time_up_result
            remaining_lives = current_lives - 1
            if remaining_lives > 0:
                choice = _handle_times_up(surface)
            else:
                choice = "done"
            _cleanup_ecs()
            if choice == "retry":
                # Relancer le même niveau avec une vie en moins
                maze, cols, rows = _init_level(
                    current_score, current_level,
                    level_seeds[current_level],
                    remaining_lives,
                )
                if cheat_active:
                    _apply_cheat_invincibility()
                continue
            else:
                # Done ou plus de vies → écran de game over
                page, pseudo = run_game_over(
                    surface, current_score,
                )
                save_highscore(
                    pseudo if pseudo else "???",
                    current_score,
                )
                return page

        # F. VÉRIFICATION DE NIVEAU TERMINÉ
        # Si toutes les gommes et power pellets sont
        # mangées, on passe au niveau suivant.
        result = _check_level_complete()
        if result is not None:
            current_score, current_level = result
            _cleanup_ecs()

            if current_level >= 10:
                # Victoire ! Le joueur a terminé les 10 niveaux
                page, pseudo = run_winner(surface, current_score)
                save_highscore(pseudo if pseudo else "???", current_score)
                return page

            # Niveau suivant : on garde le score et on incrémente le niveau
            next_level = current_level + 1
            maze, cols, rows = _init_level(
                current_score, next_level, level_seeds[next_level],
            )
            if cheat_active:
                _apply_cheat_invincibility()

        # F. AFFICHAGE FINAL (Flip)
        # Tout ce qu'on a dessiné (fill, draw_maze, esper.process) était fait
        # sur une image cachée (le buffer). On l'affiche maintenant à l'écran.
        pygame.display.flip()

    return page
