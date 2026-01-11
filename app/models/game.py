"""Game model module for Smart Word Ladder.

This module contains the data models for game state management.
"""

import datetime
from enum import Enum
from datetime import datetime  # Import the datetime class from the datetime module
from typing import List, Optional
from pydantic import BaseModel


class GameStatus(str, Enum):
    """Enum representing the different statuses a game can have."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ACTIVE = "active"  # Added this to match what's being used


class GameMode(str, Enum):
    """Enum representing the different game modes available."""
    CLASSIC = "CLASSIC"
    TIMED = "TIMED"


class DifficultyLevel(str, Enum):
    """Enum representing the different difficulty levels."""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class Game(BaseModel):
    """Model representing a game in the word ladder application.
    
    Attributes:
        id: Unique identifier for the game
        start_word: The starting word for the ladder
        target_word: The target word to reach
        current_word: The current word in the ladder
        moves: List of words that form the ladder so far
        status: Current status of the game
        difficulty: Difficulty level of the game
        game_mode: Mode of the game
        player_id: Optional ID of the player
        created_at: When the game was created
        time_elapsed: Time elapsed in seconds
    """
    id: str
    start_word: str
    target_word: str
    current_word: str
    moves: List[str] = []
    status: str = "active"  # Changed to string to avoid enum issues
    difficulty: DifficultyLevel
    game_mode: GameMode
    player_id: Optional[str] = None
    created_at: datetime = datetime.now()
    time_elapsed: int = 0
    
    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True