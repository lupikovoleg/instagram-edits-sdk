"""Unofficial research client; see docs/verification.md for evidence limits."""
from .client import EditsClient, QueryResult, ReelInsights, ReelsPage, RetentionPoint, Session
from ._wire import RetentionError as EditsError, media_id
from .registry import get_operation, list_operations

__version__ = "0.2.2"
__all__ = ["EditsClient", "EditsError", "QueryResult", "ReelInsights", "ReelsPage", "RetentionPoint",
           "Session", "media_id", "get_operation", "list_operations"]
