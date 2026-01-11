"""Main application module for Smart Word Ladder game.

This module initializes the FastAPI application and sets up the API endpoints.
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.core.game_engine import GameEngine
from app.core.word_validator import WordValidator
from app.nlp.word_processor import WordProcessor
from app.models.game import Game, GameMode, DifficultyLevel
from app.models.player import Player
from app.api.schemas import (
    GameCreateRequest,
    GameResponse,
    MoveRequest,
    MoveResponse,
    HintRequest,
    HintResponse,
    DailyChallengeResponse
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Word Ladder API",
    description="API for the Smart Word Ladder game",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)  # Create folder if it doesn't exist
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize game components
game_engine = GameEngine()
word_validator = WordValidator()
word_processor = WordProcessor()

# In-memory storage for active games (replace with database in production)
active_games = {}


@app.get("/")
async def read_root():
    """Serve the index.html file if it exists, otherwise return welcome message."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "Welcome to Smart Word Ladder API!"}


@app.post("/games/", response_model=GameResponse)
async def create_game(game_request: GameCreateRequest):
    """Create a new game."""
    try:
        # Create game using engine with proper parameters
        game = game_engine.create_game(
            difficulty=game_request.difficulty,
            game_mode=game_request.game_mode,
            word_length=game_request.word_length,
            player_id=game_request.player_id
        )
        
        # Store game in active games
        active_games[game.id] = game
        
        # Return game response
        return GameResponse(
            game_id=game.id,
            start_word=game.start_word,
            target_word=game.target_word,
            current_word=game.current_word,
            moves=game.moves,
            status=game.status,
            difficulty=game.difficulty,
            game_mode=game.game_mode,
            created_at=game.created_at.isoformat(),
            time_elapsed=game.time_elapsed,
            word_length=len(game.start_word)
        )
    except Exception as e:
        logger.error(f"Error creating game: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/games/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    """Get the current state of a game."""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[game_id]
    return GameResponse(
        game_id=game.id,
        start_word=game.start_word,
        target_word=game.target_word,
        current_word=game.current_word,
        moves=game.moves,
        status=game.status,
        difficulty=game.difficulty,
        game_mode=game.game_mode,
        created_at=game.created_at.isoformat(),
        time_elapsed=game.time_elapsed,
        word_length=len(game.start_word)
    )


@app.post("/games/{game_id}/move", response_model=MoveResponse)
async def make_move(game_id: str, move_request: MoveRequest):
    """Make a move in the game by submitting a new word."""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[game_id]
    
    try:
        # Make move using game engine
        result = game_engine.make_move(game, move_request.word)
        
        return MoveResponse(
            valid=True,
            word=move_request.word,
            is_target=result.is_target,
            moves_count=result.moves_count,
            path=result.path,
            message=result.message
        )
    except ValueError as e:
        # Handle invalid move
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error making move: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/games/{game_id}/hint", response_model=HintResponse)
async def get_hint(game_id: str, hint_request: HintRequest):
    """Get a hint for the current game state."""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[game_id]
    
    try:
        hint = game_engine.get_hint(game, hint_request.hint_level)
        return HintResponse(
            hint_type=hint.hint_type.value,
            hint_text=hint.hint_text,
            suggested_letter=hint.suggested_letter,
            position=hint.position
        )
    except Exception as e:
        logger.error(f"Error getting hint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/daily-challenge", response_model=DailyChallengeResponse)
async def get_daily_challenge():
    """Get the daily challenge puzzle."""
    try:
        challenge = game_engine.get_daily_challenge()
        return DailyChallengeResponse(
            date=challenge["date"],
            start_word=challenge["start_word"],
            target_word=challenge["target_word"],
            difficulty=challenge["difficulty"],
            theme=challenge["theme"]
        )
    except Exception as e:
        logger.error(f"Error getting daily challenge: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)