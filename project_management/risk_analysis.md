# Risk Analysis

## Identified Risks and Mitigation

| # | Risk | Probability | Impact | Mitigation | Outcome |
|---|------|-------------|--------|------------|---------|
| 1 | **Maze generation too slow for large mazes** | Medium | High | Used recursive DFS with bitmask representation for efficiency. | No performance issues encountered. |
| 2 | **Ghost AI too hard or too easy** | High | Medium | Mixed BFS pathfinding (70%) with random movement (30%) for unpredictability. 4 different strategies for variety. | Balanced gameplay achieved. |
| 3 | **Config file invalid or corrupted** | Medium | High | Parser validates all values with type checks and range checks. Falls back to sensible defaults for any invalid or missing value. | Robust: game always starts even with bad config. |
| 4 | **Short development timeline (2 weeks)** | High | High | Clear task split between team members. Focused on core features first (maze, movement, collision) before polish (lives, levels, screens). | Delivered on time with all planned features. |
| 5 | **Integration issues between parser and game** | Medium | Medium | Agreed on config data structure early. Parser returns a standardized dictionary with guaranteed keys. | Smooth integration with minimal fixes needed. |
| 6 | **Collision detection edge cases** | Medium | Medium | Invincibility frames (120 frames) after losing a life to prevent instant re-death. Distance-based collision with tuned thresholds. | Resolved: no unfair deaths. |
| 7 | **Highscore file corruption** | Low | Low | JSON format is simple and human-readable. File is rewritten entirely on each save (no partial updates). | No issues encountered. |

## Risk Matrix

```
            Low Impact    Medium Impact    High Impact
High Prob                    R2               R4
Med Prob       R7            R5, R6           R1, R3
Low Prob
```
