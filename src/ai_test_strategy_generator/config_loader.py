"""Load non-secret configuration from a YAML file and environment variables.

Resolution order (later wins):
  1. Built-in defaults (via ProviderConfig)
  2. Config file (strategy.config.yaml or user-supplied path)
  3. Environment variables (STRATEGY_LLM_* prefix)

Security rules:
  - api_key, tokens, and passwords MUST NOT appear in the config file.
  - If api_key is found in the config file, emit a UserWarning and ignore it.
  - api_key is only sourced from STRATEGY_LLM_API_KEY env var.
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Any

import yaml

_DEFAULTS: dict[str, Any] = {
    "provider": "ollama",
    "model": "glm4:latest",
    "base_url": "http://localhost:11434",
    "temperature": 0.0,
    "max_tokens": 4096,
}

_FORBIDDEN_FILE_KEYS: frozenset[str] = frozenset(
    {"api_key", "token", "password", "secret", "credential"}
)

_ENV_VAR_MAP: dict[str, tuple[str, type]] = {
    "STRATEGY_LLM_PROVIDER": ("provider", str),
    "STRATEGY_LLM_MODEL": ("model", str),
    "STRATEGY_LLM_BASE_URL": ("base_url", str),
    "STRATEGY_LLM_TEMPERATURE": ("temperature", float),
    "STRATEGY_LLM_MAX_TOKENS": ("max_tokens", int),
}


def load_config(path: Path | None) -> dict[str, Any]:
    """Return a merged configuration dict (non-secret keys only).

    Parameters
    ----------
    path:
        Path to a YAML config file.  ``None`` or a non-existent path silently
        falls back to built-in defaults.

    Returns
    -------
    dict
        Keys: provider, model, base_url, temperature, max_tokens.
        ``api_key`` is intentionally absent — callers must read it from the
        ``STRATEGY_LLM_API_KEY`` environment variable.
    """
    config: dict[str, Any] = dict(_DEFAULTS)

    # Layer 2 — config file
    if path is not None and path.exists():
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            warnings.warn(
                f"Could not parse config file {path}: {exc}. Using defaults.",
                stacklevel=2,
            )
            raw = {}

        for key, value in raw.items():
            if key in _FORBIDDEN_FILE_KEYS:
                warnings.warn(
                    f"'{key}' found in config file {path} — "
                    "secret values must be supplied via environment variables. "
                    "This entry has been ignored.",
                    stacklevel=2,
                )
                continue
            config[key] = value

    # Layer 3 — environment variables
    for env_var, (config_key, cast) in _ENV_VAR_MAP.items():
        raw_value = os.environ.get(env_var)
        if raw_value is not None:
            try:
                config[config_key] = cast(raw_value)
            except (ValueError, TypeError) as exc:
                warnings.warn(
                    f"Environment variable {env_var}={raw_value!r} could not be cast "
                    f"to {cast.__name__}: {exc}. Using previous value.",
                    stacklevel=2,
                )

    return config
