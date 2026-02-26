# Team Organization

## Members

| Name | Role | Responsibilities |
|------|------|-----------------|
| **poliver** | Game developer | ECS architecture, gameplay, ghost AI, maze, rendering, screens, utils |
| **arouxel** | Data & tooling | JSON parser, config validation, highscore I/O, error handling, project setup |

## Task Split

The work was divided by domain expertise:

- **poliver** handled all game-related code: the ECS framework integration (esper), all processors (input, movement, ghost AI, collision, render), maze generation wrapper, screen flow (menu, game, instructions, game over, highscores), and utility functions (BFS pathfinding, coordinate conversion).

- **arouxel** handled all data-related code: the JSON configuration parser with full validation and default fallback values, highscore file read/write, the project tooling setup (pyproject.toml, Makefile, uv configuration), and error handling across the codebase.

## Decision Making

- Decisions were made through direct communication between team members.
- Architecture choices (ECS pattern, pygame-ce, esper library) were decided together at the start.
- Each member had autonomy over their own domain.

## Collaboration Tools

| Tool | Purpose |
|------|---------|
| Git / GitHub | Version control, code sharing |
| Direct communication | Daily coordination, decisions |

## Commit Summary by Author

| Author | Commits | Key contributions |
|--------|---------|-------------------|
| poliver (Bluerise) | 7 | Game logic, ECS, maze, AI, lives, screens |
| arouxel (Itsoon) | 5 | Parser, config, highscore, project setup |
