"""Connectors Feature - Integração com sistemas externos."""

from .base import BaseConnector
from .confluence import ConfluenceClient, ConfluencePage

__all__ = ["BaseConnector", "ConfluenceClient", "ConfluencePage"]
