# Project Timeline

## Overview

- **Start date**: 2026-02-10 (project kickoff & planning)
- **End date**: 2026-02-24 (final delivery)
- **Duration**: 2 weeks
- **Team**: poliver, arouxel

## Kanban Board (final state)

### Done

| Task | Assignee | Priority | Status |
|------|----------|----------|--------|
| Project setup (uv, pyproject.toml, Makefile) | arouxel | High | Done |
| Maze generation algorithm (DFS) | arouxel | High | Done |
| Maze rendering (bitmask walls) | poliver | High | Done |
| ECS architecture (esper integration) | poliver | High | Done |
| Player input & grid movement | poliver | High | Done |
| Ghost AI (4 strategies + BFS) | poliver | High | Done |
| Collision detection (dots, ghosts) | poliver | High | Done |
| Power pellets & ghost vulnerability | poliver | Medium | Done |
| Score system | poliver | Medium | Done |
| Lives system & invincibility frames | poliver | Medium | Done |
| Level progression (10 levels) | poliver | Medium | Done |
| Screen navigation (menu, game, game over) | poliver | Medium | Done |
| Instructions screen | poliver | Low | Done |
| JSON config parser with validation | arouxel | High | Done |
| Config default values & error handling | arouxel | High | Done |
| Highscore persistence (JSON I/O) | arouxel | Medium | Done |
| Highscore display screen | poliver | Medium | Done |
| Name input after game over | poliver | Low | Done |
| Timer per level | poliver | Medium | Done |
| README & documentation | both | Low | Done |
| Project management docs | both | Low | Done |

## Gantt Chart

```
Week 1 (Feb 10 – Feb 16)        Week 2 (Feb 17 – Feb 24)
Mon Tue Wed Thu Fri Sat Sun      Mon Tue Wed Thu Fri Sat Sun Mon
 10  11  12  13  14  15  16       17  18  19  20  21  22  23  24

poliver:
 [====== Maze gen & render ====]
                  [====== ECS + Input + Movement ======]
                                  [==== Ghost AI + Collision ====]
                                            [= Pellets, Lives, Levels =]
                                                      [= Screens + Polish =]

arouxel:
 [== Setup ==]
        [======= JSON parser + validation =======]
                                  [=== Highscore I/O + error handling ===]
                                                            [= Integration =]

both:
                                                               [= Docs + PM =]
```

## Progress Tracking

| Week | Planned | Actual | Notes |
|------|---------|--------|-------|
| Week 1 | Maze, ECS foundation, parser | Maze gen done, ECS started, parser started | On track |
| Week 2 | AI, collision, screens, integration | All features implemented, integration done | Completed on time |
