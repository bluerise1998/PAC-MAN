import pygame

MENU_OPTIONS = ["Start Game", "View Highscores", "Instructions", "Exit"]


def draw_title(surface: pygame.Surface) -> None:
    """Dessine le titre PAC MAN en jaune, centré en haut.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
    """
    # Initialisation de la Police (Font) :
    # - Arg 1 (None) : On utilise la police par défaut de Pygame.
    # - Arg 2 (74)   : La taille de la police en pixels (hauteur).
    font = pygame.font.Font(None, 74)
    # RENDER : Transforme le texte (String) en une
    # Image (Surface) que Pygame peut afficher.
    # - Arg 1 : Le texte à écrire ("PAC MAN").
    # - Arg 2 : Antialiasing (True) -> Lisse les bords
    # pour que ce soit moins pixelisé (plus joli).
    # - Arg 3 : La couleur du texte (R, G, B)
    # -> Ici (255, 255, 0) = Jaune.
    title = font.render("PAC MAN", True, (255, 255, 0))

    # BLIT (Block Image Transfer) : C'est la fonction
    # "Copier-Coller" de Pygame.
    # Elle prend 2 arguments : QUOI dessiner (Source)
    # et OÙ dessiner (Destination).
    #
    # PROBLÈME : blit() est "bête", il ne sait dessiner
    # qu'à partir du coin HAUT-GAUCHE.
    # Si on lui donne (400, 100), le texte commencera
    # à 400 et ira vers la droite (pas centré).
    #
    # SOLUTION : .get_rect(center=(400, 100)) est une calculatrice automatique.
    # 1. Elle crée un rectangle de la taille exacte du texte.
    # 2. Elle place le CENTRE de ce rectangle sur (400, 100).
    # 3. Elle calcule pour nous où tombe le coin haut-gauche (ex: 300, 75).
    # C'est ce coin haut-gauche calculé que blit() utilise pour dessiner.
    surface.blit(title, title.get_rect(center=(400, 100)))


def draw_options(surface: pygame.Surface, cursor: int) -> None:
    """Dessine les options du menu. Jaune si sélectionnée.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        cursor: Index de l'option actuellement sélectionnée.
    """
    font = pygame.font.Font(None, 50)
    for i, option in enumerate(MENU_OPTIONS):
        # Opérateur ternaire : Si c'est l'option
        # sélectionnée (cursor), on met Jaune,
        # sinon Blanc.
        color = (255, 255, 0) if i == cursor else (255, 255, 255)
        text = font.render(option, True, color)
        surface.blit(text, text.get_rect(center=(400, 250 + i * 70)))


def draw_menu(surface: pygame.Surface, cursor: int) -> None:
    """Dessine tout le menu : titre + options.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        cursor: Index de l'option actuellement sélectionnée.
    """
    draw_title(surface)
    draw_options(surface, cursor)


def handle_menu_input(events: list[pygame.event.Event], cursor: int) -> int:
    """Lit les flèches haut/bas et retourne le nouveau cursor.

    Args:
        events: Liste des événements Pygame de la frame.
        cursor: Index actuel du curseur.

    Returns:
        int: Le nouvel index du curseur après navigation.
    """
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                cursor = (cursor - 1) % len(MENU_OPTIONS)
            elif event.key == pygame.K_DOWN:
                cursor = (cursor + 1) % len(MENU_OPTIONS)
    return cursor


def check_menu_confirm(
    events: list[pygame.event.Event], cursor: int,
) -> str | None:
    """Retourne l'option si Entrée est pressé, sinon None.

    Args:
        events: Liste des événements Pygame de la frame.
        cursor: Index actuel du curseur.

    Returns:
        str | None: Le nom de l'option sélectionnée ou None.
    """
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return MENU_OPTIONS[cursor]
    return None


def run_menu(surface: pygame.Surface, page: str) -> str:
    """Boucle du menu. Retourne le nom de l'option choisie.

    Args:
        surface: La surface Pygame sur laquelle dessiner.
        page: Page courante (doit être "menu").

    Returns:
        str: Le nom de l'option sélectionnée ou "Exit".
    """
    cursor = 0

    while page == "menu":
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                return "Exit"

        cursor = handle_menu_input(events, cursor)
        selected = check_menu_confirm(events, cursor)

        if selected is not None:
            page = selected

        # 1. On efface tout (écran noir) sur l'image cachée (Back Buffer).
        #    On ne le voit pas clignoter car ce n'est
        #    pas encore affiché à l'écran.
        surface.fill((0, 0, 0))
        draw_menu(surface, cursor)

        # 2. On affiche l'image finale d'un seul coup (Flip).
        #    L'ancienne image est remplacée instantanément
        #    par la nouvelle (déjà dessinée).
        pygame.display.flip()

    return page
