"""Hint model module for Smart Word Ladder.

This module contains the data models for hint generation and management.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class HintType(str, Enum):
    """Enum representing the different types of hints available."""
    GENERAL = "general"    # General game hints
    SEMANTIC = "semantic"  # Semantic hints about the word meaning
    POSITION = "position"  # Hints about which position to change
    LETTER = "letter"      # Specific letter change suggestions


class Hint(BaseModel):
    """Model representing a hint in the word ladder game.
    
    Attributes:
        hint_type: The type of hint being provided
        hint_text: The text of the hint
        position: Optional position in the word to change (for position/letter hints)
        suggested_letter: Optional suggested letter (for letter hints)
    """
    hint_type: HintType
    hint_text: str
    position: Optional[int] = None
    suggested_letter: Optional[str] = None