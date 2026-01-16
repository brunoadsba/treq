"""Connectors Feature - Integração com sistemas externos."""

from .base import BaseConnector
from .confluence import ConfluenceClient, ConfluencePage
from .slack import SlackClient, SlackMessage, SlackChannel

__all__ = [
    "BaseConnector",
    "ConfluenceClient", "ConfluencePage",
    "SlackClient", "SlackMessage", "SlackChannel"
]
