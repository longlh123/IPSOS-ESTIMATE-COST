# database/__init__.py
# -*- coding: utf-8 -*-
"""
Database module for the Project Cost Calculator application.
Handles database connections and operations.
"""

from .db_manager import DatabaseManager

__all__ = ['DatabaseManager']