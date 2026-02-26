# Project Summary & Retrospective

## Project Overview

- **Project**: Pac-Man game in Python (pygame-ce + esper ECS)
- **Team**: poliver, arouxel
- **Duration**: 2 weeks (Feb 10 – Feb 24, 2026)
- **Result**: Fully functional Pac-Man game delivered on time

## What Went Well

- **Clear task separation**: Splitting game logic (poliver) and data/parser (arouxel) avoided merge conflicts and allowed parallel work.
- **ECS architecture**: Using the Entity Component System pattern made adding features (lives, invincibility, levels) straightforward without refactoring existing code.
- **Parser robustness**: The config parser handles all edge cases gracefully with defaults, so the game always runs regardless of config quality.

## Challenges Encountered

| Challenge | Resolution |
|-----------|------------|
| Lives decreasing instantly from single ghost hit | Added invincibility frames component (120 frames cooldown) |
| Integrating parser output with game expectations | Agreed on a standardized config dictionary format early |
| Balancing ghost difficulty | Mixed BFS (70%) with random movement (30%) for fair gameplay |
| Short timeline for full game | Prioritized core mechanics first, then added polish features |

## Blocking Points

No major blocking points were encountered. The clear task separation meant each team member could work independently most of the time. The only coordination needed was for the config dictionary interface between parser and game, which was resolved quickly through direct communication.

## Key Technical Choices

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| Architecture | ECS (esper) | Clean separation of concerns, easy to add new features |
| Rendering | pygame-ce | Mature 2D game library, good documentation |
| Config format | JSON | Simple, human-readable, native Python support |
| Maze algorithm | Recursive DFS | Generates good mazes, seed-reproducible |
| Pathfinding | BFS | Guaranteed shortest path, simple to implement |
| Highscores | JSON flat file | No external dependencies, sufficient for 10 entries |

## Final Deliverables

- Playable Pac-Man game with 10 levels
- 4 ghost AI strategies
- Procedurally generated mazes (seeded)
- JSON config with full validation
- Persistent highscore system
- Complete documentation (README)
- Project management documentation
