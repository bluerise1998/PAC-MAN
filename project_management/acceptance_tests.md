# Acceptance Test Plan

## Test Categories

### 1. Maze Generation

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 1.1 | Launch game with default config | Maze displays correctly with walls, dots, and pellets | Pass |
| 1.2 | Launch with same seed twice | Identical maze layout both times | Pass |
| 1.3 | Launch with seed = 0 | Random maze each time | Pass |
| 1.4 | Progress through levels 1-10 | Maze size increases each level | Pass |

### 2. Player Movement

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 2.1 | Press arrow keys | Pac-Man moves in the corresponding direction | Pass |
| 2.2 | Move into a wall | Pac-Man stops, does not clip through | Pass |
| 2.3 | Move over a dot | Dot disappears, score increases | Pass |
| 2.4 | Movement is smooth | Pixel interpolation between grid cells | Pass |

### 3. Ghost AI

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 3.1 | Ghosts move through maze | Ghosts navigate without clipping walls | Pass |
| 3.2 | Ghost touches Pac-Man | Player loses a life | Pass |
| 3.3 | Eat power pellet | Ghosts turn vulnerable (change behavior) | Pass |
| 3.4 | Touch vulnerable ghost | Ghost is eaten, score increases by ghost point value | Pass |

### 4. Lives & Game Over

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 4.1 | Lose a life | Lives counter decreases, invincibility frames activate | Pass |
| 4.2 | Lose all lives | Game over screen appears | Pass |
| 4.3 | Invincibility after hit | No life lost during invincibility window | Pass |

### 5. Scoring & Highscores

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 5.1 | Eat dots and pellets | Score increases by configured point values | Pass |
| 5.2 | Game over triggers name input | Player can enter name (1-10 alpha chars) | Pass |
| 5.3 | Score saved to highscore.json | File updated with new entry, sorted, top 10 only | Pass |
| 5.4 | Highscore screen | Displays scores ranked, top score highlighted | Pass |

### 6. Configuration Parser

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 6.1 | Valid config.json | All values loaded correctly | Pass |
| 6.2 | Missing fields in config | Default values used for missing fields | Pass |
| 6.3 | Invalid values (out of range) | Defaults applied, no crash | Pass |
| 6.4 | Malformed JSON | Error handled gracefully | Pass |
| 6.5 | No config file argument | Default config.json used | Pass |
| 6.6 | Config with comments (#) | Comments stripped, values parsed | Pass |

### 7. Screens & Navigation

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 7.1 | Main menu displays | 4 options: Start, Highscores, Instructions, Exit | Pass |
| 7.2 | Navigate menu with arrows | Selection moves up/down | Pass |
| 7.3 | Press Enter on Start | Game begins | Pass |
| 7.4 | Press Escape during game | Returns to menu | Pass |
| 7.5 | Press Space during game | Game pauses/unpauses | Pass |

### 8. Level Progression

| # | Test | Expected Result | Status |
|---|------|-----------------|--------|
| 8.1 | Eat all dots in a level | Advances to next level | Pass |
| 8.2 | Timer runs out | Level ends (game over) | Pass |
| 8.3 | Complete level 10 | Victory / game ends | Pass |

## Bugs Found and Fixed

| # | Bug | Severity | Fix | Status |
|---|-----|----------|-----|--------|
| B1 | Lives decreasing multiple times from single ghost contact | High | Added invincibility component | Fixed |
| B2 | Big pellets not awarding correct points | Medium | Fixed collision value for super pac-gums | Fixed |
| B3 | Name input screen appearing at wrong time | Low | Changed screen flow: game over -> name input | Fixed |
