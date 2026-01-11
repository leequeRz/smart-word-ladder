"""Player model module for Smart Word Ladder.

This module contains the data model for player information.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Player(BaseModel):
    """Model representing a player in the word ladder game.
    
    Attributes:
        id: Unique identifier for the player
        username: Player's username
        email: Player's email address
        created_at: When the player account was created
        games_played: Number of games played
        games_won: Number of games won
        best_score: Player's best score
        last_login: When the player last logged in
    """
    id: str
    username: str
    email: Optional[str] = None
    created_at: datetime = datetime.now()
    games_played: int = 0
    games_won: int = 0
    best_score: Optional[int] = None
    last_login: Optional[datetime] = None