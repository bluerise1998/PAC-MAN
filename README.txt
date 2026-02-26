PAC-MAN 42
==========

How to play
-----------
Run the "pacman" executable.

Controls
--------
Arrow keys   Move Pac-Man
Up / Down    Navigate menus
Enter        Select menu option
Space        Pause / Unpause
Escape       Return to menu
C            Toggle cheat mode (speed boost + invincibility)
N            Skip to next level

Gameplay
--------
- Eat all dots and power pellets to complete a level.
- Power pellets make ghosts vulnerable (blue) for 10 seconds.
- Eat vulnerable ghosts for bonus points.
- Avoid normal ghosts or you lose a life.
- Complete 10 levels to win.
- Each level has a time limit. When time runs out you can retry or quit.

Configuration
-------------
Edit config.json to customize the game:

  lives              Starting lives (default: 3)
  seed               Maze generation seed (default: 42, 0 = random)
  level_max_time     Time limit per level in seconds (default: 90)
  points_per_pacgum  Points per dot (default: 10)
  points_per_ghost   Points per ghost eaten (default: 200)

Created by poliver & arouxel - 42 School
