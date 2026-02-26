from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Defaults ────────────────────────────────────────────────────────────────

DEFAULT_LEVEL = {
    "width": 28,
    "height": 31,
}

DEFAULTS: dict[str, Any] = {
    "highscore_filename": "highscore.json",
    "lives": 3,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 100,
    "seed": 42,
    "level_max_time": 140,
    "levels": [DEFAULT_LEVEL],
}

# ── Validation helpers ───────────────────────────────────────────────────────


def _clamp_int(
    value: Any, key: str,
    min_val: int, max_val: int, default: int,
) -> int:
    """Return value clamped to [min_val, max_val],
    falling back to default on error.

    Args:
        value: La valeur à convertir et clamper.
        key: Nom de la clé de configuration (pour les logs).
        min_val: Valeur minimale autorisée.
        max_val: Valeur maximale autorisée.
        default: Valeur par défaut si conversion impossible.

    Returns:
        int: La valeur clampée dans [min_val, max_val].
    """
    try:
        v = int(value)
    except (TypeError, ValueError):
        logger.warning(
            "Config: '%s' = %r is not a valid integer — using default %r",
            key,
            value,
            default,
        )
        return default
    if v < min_val:
        logger.warning(
            "Config: '%s' = %d is below minimum %d — clamping", key, v, min_val
        )
        return min_val
    if v > max_val:
        logger.warning(
            "Config: '%s' = %d is above maximum %d — clamping", key, v, max_val
        )
        return max_val
    return v


def _validate_level(raw: object, index: int) -> dict[str, int]:
    """Validate a single level entry, returning a safe dict.

    Args:
        raw: L'objet brut lu depuis le JSON.
        index: Index du niveau dans la liste (pour les logs).

    Returns:
        dict[str, int]: Dictionnaire validé avec les clés "width" et "height".
    """
    if not isinstance(raw, dict):
        logger.warning(
            "Config: levels[%d] is not an object — using default level", index
        )
        return dict(DEFAULT_LEVEL)
    level = {}
    level["width"] = _clamp_int(
        raw.get("width", DEFAULT_LEVEL["width"]),
        f"levels[{index}].width",
        10,
        256,
        DEFAULT_LEVEL["width"],
    )
    level["height"] = _clamp_int(
        raw.get("height", DEFAULT_LEVEL["height"]),
        f"levels[{index}].height",
        10,
        256,
        DEFAULT_LEVEL["height"],
    )
    # Forward-compatibility: ignore unknown keys silently
    return level


# ── Public API ───────────────────────────────────────────────────────────────


def load_config(path: str | Path = "config.json") -> dict:
    """Load and validate the game configuration from *path*.

    Missing file, invalid JSON, or invalid values are handled gracefully
    with warnings/errors logged and defaults applied.

    Args:
        path: Chemin vers le fichier de configuration JSON.

    Returns:
        dict: La configuration validée avec les valeurs par défaut appliquées.
    """
    path = Path(path)

    # ── Read file ────────────────────────────────────────────────────────────
    try:
        raw_text = path.read_text(encoding="utf-8")
        print(f"Config: file '{path}' found")
    except FileNotFoundError:
        logger.warning(
            "Config: file '%s' not found — using all defaults", path
        )
        return dict(DEFAULTS)
    except OSError as exc:
        logger.error(
            "Config: cannot read '%s': %s — using all defaults", path, exc
        )
        return dict(DEFAULTS)

    # ── Strip comments & parse JSON ──────────────────────────────────────────
    # On retire les lignes qui commencent par # (commentaires)
    # Le fichier original n'est pas modifié, c'est juste en mémoire
    lines = raw_text.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        cleaned_lines.append(line)
    clean_text = "\n".join(cleaned_lines)

    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError as exc:
        logger.error(
            "Config: JSON parse error in '%s': %s — using all defaults",
            path,
            exc,
        )
        return dict(DEFAULTS)

    if not isinstance(data, dict):
        logger.error(
            "Config: root value in '%s' must be a JSON"
            " object — using all defaults",
            path,
        )
        return dict(DEFAULTS)

    cfg = {}

    # ── Unknown keys ─────────────────────────────────────────────────────────
    known_keys = {
        "highscore_filename",
        "lives",
        "points_per_pacgum",
        "points_per_super_pacgum",
        "points_per_ghost",
        "seed",
        "level_max_time",
        "levels",
    }
    for unknown_key in data.keys() - known_keys:
        logger.error("Config: unknown key '%s' — ignoring", unknown_key)

    # ── highscore_filename ───────────────────────────────────────────────────
    hf = data.get("highscore_filename", DEFAULTS["highscore_filename"])
    if not isinstance(hf, str) or not hf.strip():
        logger.warning(
            "Config: 'highscore_filename' is invalid — using default %r",
            DEFAULTS["highscore_filename"],
        )
        hf = DEFAULTS["highscore_filename"]
    cfg["highscore_filename"] = hf

    # ── Integers ─────────────────────────────────────────────────────────────
    cfg["lives"] = _clamp_int(
        data.get("lives", DEFAULTS["lives"]), "lives", 1, 9, DEFAULTS["lives"]
    )
    cfg["points_per_pacgum"] = _clamp_int(
        data.get("points_per_pacgum", DEFAULTS["points_per_pacgum"]),
        "points_per_pacgum",
        0,
        99999,
        DEFAULTS["points_per_pacgum"],
    )
    cfg["points_per_super_pacgum"] = _clamp_int(
        data.get(
            "points_per_super_pacgum", DEFAULTS["points_per_super_pacgum"]
        ),
        "points_per_super_pacgum",
        0,
        99999,
        DEFAULTS["points_per_super_pacgum"],
    )
    cfg["points_per_ghost"] = _clamp_int(
        data.get("points_per_ghost", DEFAULTS["points_per_ghost"]),
        "points_per_ghost",
        0,
        99999,
        DEFAULTS["points_per_ghost"],
    )
    cfg["seed"] = _clamp_int(
        data.get("seed", DEFAULTS["seed"]),
        "seed",
        0,
        2**31 - 1,
        DEFAULTS["seed"],
    )
    cfg["level_max_time"] = _clamp_int(
        data.get("level_max_time", DEFAULTS["level_max_time"]),
        "level_max_time",
        10,
        3600,
        DEFAULTS["level_max_time"],
    )

    # ── Levels array ─────────────────────────────────────────────────────────
    raw_levels = data.get("levels", DEFAULTS["levels"])
    if not isinstance(raw_levels, list) or len(raw_levels) == 0:
        logger.warning(
            "Config: 'levels' must be a non-empty array — using default level"
        )
        raw_levels = DEFAULTS["levels"]
    cfg["levels"] = [
        _validate_level(lvl, i) for i, lvl in enumerate(raw_levels)
    ]

    return cfg


# ── Singleton ────────────────────────────────────────────────────────────────

config: dict = dict(DEFAULTS)


def init_config(path: str | Path = "config.json") -> None:
    """Load config from *path* into the module-level singleton.

    Args:
        path: Chemin vers le fichier de configuration JSON.
    """
    config.clear()
    config.update(load_config(path))
