"""API schema definitions for Smart Word Ladder.

This module contains Pydantic models for API request and response schemas.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.game import GameMode, DifficultyLevel


class GameCreateRequest(BaseModel):
    """Request schema for creating a new game."""
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM  # Default value
    game_mode: GameMode = GameMode.CLASSIC  # Default value
    word_length: int = 4  # Default value, เพิ่ม field นี้ให้ตรงกับ frontend
    player_id: Optional[str] = None
    # ลบ start_word และ target_word ออกเพราะระบบจะสุ่มเอง


class GameResponse(BaseModel):
    """Response schema for game data."""
    game_id: str
    start_word: str
    target_word: str
    current_word: str
    moves: List[str]
    status: str
    difficulty: DifficultyLevel
    game_mode: GameMode
    created_at: str  # เปลี่ยนเป็น str เพื่อหลีกเลี่ยงปัญหาการ serialize
    time_elapsed: int
    word_length: Optional[int] = None  # เพิ่ม field นี้


class MoveRequest(BaseModel):
    """Request schema for making a move."""
    word: str


class MoveResponse(BaseModel):
    """Response schema for move results."""
    valid: bool
    word: str
    is_target: bool
    moves_count: int
    path: List[str]
    message: str


class HintRequest(BaseModel):
    """Request schema for getting a hint."""
    hint_level: int = 1


class HintResponse(BaseModel):
    """Response schema for hint data."""
    hint_type: str
    hint_text: str
    position: Optional[int] = None
    suggested_letter: Optional[str] = None


class DailyChallengeResponse(BaseModel):
    """Response schema for daily challenge data."""
    date: str  # เปลี่ยนเป็น str
    start_word: str
    target_word: str
    difficulty: DifficultyLevel
    theme: Optional[str] = None