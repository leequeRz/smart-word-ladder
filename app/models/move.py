"""Move model module for Smart Word Ladder.

This module contains the data models for move results and validation.
"""

from typing import List
from pydantic import BaseModel


class MoveResult(BaseModel):
    """Model representing the result of a move in the word ladder game.
    
    Attributes:
        is_target: Whether the move reached the target word
        moves_count: Number of moves made so far
        path: List of words forming the current path
        message: Feedback message for the player
    """
    is_target: bool
    moves_count: int
    path: List[str]
    message: str