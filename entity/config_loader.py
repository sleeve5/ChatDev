"""Helpers for loading validated configuration objects."""

from pathlib import Path
from typing import Any, Mapping, MutableMapping

import yaml

from entity.configs import DesignConfig, ConfigError
from utils.env_loader import load_dotenv_file, build_env_var_map
from utils.vars_resolver import resolve_design_placeholders


def apply_model_override(data: Any, model_name: str | None) -> None:
    """Override OpenAI agent models without rewriting workflow templates."""
    if not model_name:
        return
    if isinstance(data, list):
        for item in data:
            apply_model_override(item, model_name)
        return
    if not isinstance(data, MutableMapping):
        return

    config = data.get("config")
    if data.get("type") == "agent" and isinstance(config, MutableMapping):
        if config.get("provider") == "openai":
            config["name"] = model_name
    for value in data.values():
        apply_model_override(value, model_name)


def prepare_design_mapping(data: Mapping[str, Any], *, source: str | None = None) -> Mapping[str, Any]:
    load_dotenv_file()
    env_lookup = build_env_var_map()
    prepared = dict(data)
    resolve_design_placeholders(prepared, env_lookup=env_lookup, path=source or "root")
    apply_model_override(prepared, env_lookup.get("MODEL_NAME"))
    return prepared


def load_design_from_mapping(data: Mapping[str, Any], *, source: str | None = None) -> DesignConfig:
    """Parse a raw dictionary into a typed :class:`DesignConfig`."""
    prepared = prepare_design_mapping(data, source=source)
    return DesignConfig.from_dict(prepared, path="root")


def load_design_from_file(path: Path) -> DesignConfig:
    """Read a YAML file and parse it into a :class:`DesignConfig`."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.load(handle, Loader=yaml.FullLoader)
    if not isinstance(data, Mapping):
        raise ConfigError("YAML root must be a mapping", path=str(path))
    return load_design_from_mapping(data, source=str(path))
