"""Versioned APK operation catalog, not a list of verified server endpoints."""
from functools import lru_cache
from importlib.resources import files
import copy
import json

from ._wire import RetentionError


@lru_cache(maxsize=1)
def _operations():
    return {item["operation_name"]: item for item in json.loads(
        files("edits_api").joinpath("operations.json").read_text(encoding="utf-8"))}


def get_operation(name):
    try:
        return copy.deepcopy(_operations()[name])
    except KeyError as exc:
        raise RetentionError(f"Unknown operation: {name}") from exc


def list_operations(*, edits_only=False):
    return [copy.deepcopy(item) for item in _operations().values()
            if not edits_only or item["edits_related"]]
