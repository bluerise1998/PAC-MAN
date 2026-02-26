*This project has been created as part of the 42 curriculum by poliver, arouxel.*

# Pac-Man

A fully playable Pac-Man game built in Python using Pygame and an Entity Component System (ECS) architecture. Navigate procedurally generated mazes, eat pellets, avoid ghosts, and climb through 10 increasingly challenging levels.

## Description

This project is a recreation of the classic Pac-Man arcade game. The player controls Pac-Man through a maze, eating dots (pac-gums) and power pellets (super pac-gums) while avoiding ghosts controlled by different AI strategies. Eating a power pellet makes ghosts vulnerable for a limited time, allowing the player to eat them for bonus points.

Key features:
- Procedurally generated mazes using a recursive depth-first search algorithm with a configurable seed
- 4 ghosts with distinct AI behaviors (direct chase, horizontal intercept, vertical intercept, pincer attack) powered by BFS pathfinding
- 10 levels with increasing maze dimensions
- Persistent highscore system (top 10)
- Fully configurable gameplay through a JSON config file
- Lives, score, timer, and level progression
- Smooth movement interpolation between grid cells

## Instructions

### Requirements

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
make install
```

Or manually:

```bash
uv sync
```

### Running the game

```bash
make run
```

Or with a custom configuration file:

```bash
uv run pac-man.py path/to/config.json
```

### Controls

| Key | Action |
|-----|--------|
| Arrow keys | Move Pac-Man |
| Up / Down | Navigate menus |
| Enter | Select menu option |
| Space | Pause / Unpause |
| Escape | Return to menu |
| C | Toggle cheat mode (speed boost + invincibility) |
| N | Skip to next level (debug) |

### Building for distribution (itch.io)

Requires PyInstaller (`uv add pyinstaller` if not already installed).

```bash
uv run pyinstaller pacman.spec --distpath dist --workpath build && mkdir -p dist/pacman-linux && cp dist/pacman dist/pacman-linux/ && cp config.json README.txt dist/pacman-linux/ && zip -rj dist/pacman-linux.zip dist/pacman-linux/ && rm -rf dist/pacman dist/pacman-linux build
```

The resulting `dist/pacman-linux.zip` can be uploaded directly to itch.io.

### Other Makefile targets

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make run` | Run the game |
| `make debug` | Run with Python debugger |
| `make clean` | Remove cache files |
| `make lint` | Run flake8 and mypy |
| `make lint-strict` | Run strict type checking |

## Configuration

The game reads a JSON configuration file (`config.json` by default, or a path passed as a CLI argument). A template is provided in `config.example.json`.

### Config file structure

```json
{
  "highscore_filename": "highscore.json",
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "lives": 3,
  "seed": 42,
  "level_max_time": 90
}
```

### Parameters and defaults

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `highscore_filename` | string | `"highscore.json"` | — | Path to the highscore JSON file |
| `points_per_pacgum` | int | 10 | 0–99,999 | Points awarded per dot |
| `points_per_super_pacgum` | int | 50 | 0–99,999 | Points awarded per power pellet |
| `points_per_ghost` | int | 200 | 0–99,999 | Points awarded per vulnerable ghost eaten |
| `lives` | int | 3 | 1–9 | Starting number of lives |
| `seed` | int | 42 | 0–2,147,483,647 | Seed for maze generation (0 = random) |
| `level_max_time` | int | 90 | 10–3,600 | Time limit per level in seconds |
| `levels` | array | 3 entries | — | List of level definitions (width/height, 10–256 each) |

The parser strips comment lines (starting with `#`), validates all values, and falls back to sensible defaults when a value is missing or invalid.

## Highscore

Scores are stored in a JSON file (path defined in the config, default: `highscore.json`). The file contains a sorted array of `{ "name": "...", "score": ... }` objects, keeping only the top 10 entries.

After a game over or victory, the player is prompted to enter their name (1–10 alphabetic characters). The score is inserted into the list, which is re-sorted in descending order and truncated to 10 entries before being saved back to disk.

We chose a simple JSON flat-file approach because:
- It requires no external database or server
- The file is human-readable and easy to inspect or edit manually
- 10 entries is a small dataset that doesn't need indexing or query capabilities
- It integrates naturally with the existing JSON-based config system

The highscore screen displays scores ranked from highest to lowest, with the top score highlighted in yellow. The current best score is also shown in the game HUD during play.

## Maze Generation

Mazes are generated using the `MazeGenerator` class (in `mazegenerator.py`), which implements a **recursive depth-first search (DFS)** algorithm with randomized neighbor traversal.

### How it works

1. **Empty maze creation**: A grid is initialized with border walls encoded as bitmasks (TOP=1, RIGHT=2, BOTTOM=4, LEFT=8). A cell value of 15 (all bits set) represents a solid block.
2. **42 easter egg**: The number "42" is embedded as solid blocks in the center of the maze (a nod to 42 school).
3. **Passage carving**: Starting from the entry cell, the algorithm recursively visits unvisited neighbors in random order, removing walls between connected cells. When `perfect=False` (default), there is a 20% chance of creating additional loops by removing walls to already-visited cells, making the maze more open and playable.
4. **Shortest path**: After generation, the algorithm finds the shortest path from entry to exit using iterative deepening.

### Integration with the game

The game wrapper (`maze/generation.py`) calls `MazeGenerator` with the dimensions and seed from the current level config. Each level can have a different maze size, and the seed ensures reproducible mazes. The generated bitmask grid is used by both the rendering system (to draw walls) and the movement/AI systems (to check wall collisions via bitwise operations).

## Implementation

### Technology stack

| Library | Version | Role |
|---------|---------|------|
| **pygame-ce** | >= 2.5.6 | Rendering, input, window management |
| **esper** | >= 3.7 | Entity Component System framework |
| **uv** | — | Package management and virtual environment |

### Core mechanics

- **Grid locking**: Both the player and ghosts can only change direction when perfectly centered on a grid cell. This prevents clipping through walls and ensures consistent, predictable movement.
- **Interpolated movement**: `GridPosition` (logical position) updates instantly, while `Position` (pixel position) interpolates toward it at 3 pixels/frame, producing smooth visual movement.
- **Collision detection**: Uses squared-distance checks between pixel positions. Different thresholds apply for dots (200), power pellets (324), and ghosts (300).
- **Invincibility frames**: After losing a life, the player is invincible for 120 frames (2 seconds) to prevent instant re-death from the same ghost.
- **Ghost vulnerability**: Eating a power pellet makes all ghosts vulnerable for 600 frames (10 seconds). Vulnerable ghosts can be eaten for bonus points and are sent back to their spawn corner.

### Ghost AI

Each ghost uses a different targeting strategy based on its ID (modulo 4):

| Ghost | Strategy | Target |
|-------|----------|--------|
| #0 | Direct chase | Player's exact position |
| #1 | Horizontal intercept | 4 cells to the right of the player |
| #2 | Vertical intercept | 4 cells below the player |
| #3 | Pincer | 4 cells up-left of the player |

Ghosts use **BFS (Breadth-First Search)** pathfinding 70% of the time and move randomly 30% of the time, introducing unpredictability. When vulnerable, ghosts flee to the corner farthest from the player.

## General Software Architecture

```
pac-man.py                  Entry point & screen navigation
    |
    +-- parser/parser.py    Config loading, validation, defaults
    |
    +-- screens/
    |     menu.py            Main menu (Start, Highscores, Instructions, Exit)
    |     game.py            Game loop, entity creation, ECS orchestration
    |     instructions.py    Controls & rules display
    |     game_over.py       End screen + name input
    |     highscores.py      Score display + persistence (JSON file I/O)
    |
    +-- ecs/
    |     components.py      Data containers (GridPosition, Sprite, Score, Lives, ...)
    |     processors/
    |         input.py       [Priority 3] Keyboard -> player GridPosition
    |         ghost_ai.py    [Priority 3] AI strategies -> ghost GridPositions
    |         movement.py    [Priority 2] GridPosition -> smooth pixel Position
    |         collision.py   [Priority 2] Interaction detection & resolution
    |         render.py      [Priority 1] Draw sprites, UI, maze
    |
    +-- maze/
    |     generation.py      Wrapper around MazeGenerator
    |     rendering.py       Bitmask -> wall drawing
    |     constants.py       Window size, margin, wall bitmask values
    |
    +-- mazegenerator.py     Recursive DFS maze generation algorithm
    +-- utils.py             Coordinate conversion, BFS pathfinding, movement helpers
```

### Data flow per frame

1. **Input**: `InputProcessor` reads keyboard state and updates the player's `GridPosition`
2. **AI**: `GhostAIProcessor` computes targets and updates each ghost's `GridPosition`
3. **Movement**: `MovementProcessor` interpolates each entity's pixel `Position` toward its `GridPosition`
4. **Collision**: `CollisionProcessor` detects and resolves interactions (eating dots, ghost encounters, timers)
5. **Render**: `RenderProcessor` draws the maze, all entities, and the HUD (score, lives, timer, level)

### Module responsibilities

| Module | Owner | Responsibility |
|--------|-------|----------------|
| `pac-man.py`, `screens/`, `ecs/`, `maze/`, `utils.py` | poliver | Game logic, ECS architecture, rendering, AI, maze integration |
| `parser/`, highscore JSON I/O, error handling | arouxel | Config parsing, validation, data persistence, error management |

## Project Management

The project was completed over a 2-week period by a team of two:

- **poliver**: Game development — ECS architecture, gameplay mechanics, ghost AI, maze rendering, screen navigation, and overall game logic.
- **arouxel**: Data management — JSON configuration parser with validation and defaults, highscore file I/O, and error handling throughout the project.

Work was coordinated through regular communication and a shared Git repository. The project management directory with detailed tracking can be found in the [project_management/](project_management/) directory.

## Play Online

The game is available to download and play on itch.io:

**[Play Pac-Man 42 on itch.io](https://adampaul42.itch.io/pac-man-42)**

## Resources

### References

- [Pygame Community Edition documentation](https://pyga.me/docs/)
- [Esper ECS library](https://github.com/benmoran56/esper)
- [The Pac-Man Dossier](https://www.gamedeveloper.com/design/the-pac-man-dossier) — detailed breakdown of original ghost AI behaviors
- [Entity Component System pattern](https://en.wikipedia.org/wiki/Entity_component_system)
- [Breadth-First Search algorithm](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Maze generation with DFS](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Depth-first_search)

### AI usage

AI tools (Claude) were used during this project for the following tasks:
- Generating this README document based on the existing codebase
- Assisting with code structuring and debugging during development
- Providing guidance on ECS architecture patterns and Pygame best practices
# PAC-MAN
