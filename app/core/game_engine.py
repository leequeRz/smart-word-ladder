"""Game Engine module for Smart Word Ladder.

This module contains the core game logic for creating and managing word ladder games.
"""

import uuid
import random
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.game import Game, GameStatus, GameMode, DifficultyLevel
from app.models.hint import Hint, HintType
from app.models.move import MoveResult
from app.core.word_validator import WordValidator
from app.nlp.word_processor import WordProcessor
from app.nlp.path_finder import PathFinder
from app.utils.word_list import get_word_pair
import logging

logger = logging.getLogger(__name__)


class GameEngine:
    """Core game engine for Smart Word Ladder.
    
    This class handles game creation, moves, hints, and daily challenges.
    """
    
    def __init__(self):
        """Initialize the game engine with required components."""
        self.word_validator = WordValidator()
        self.word_processor = WordProcessor()
        self.path_finder = PathFinder()
    
    def create_game(self, difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
                   game_mode: GameMode = GameMode.CLASSIC,
                   word_length: int = 4,
                   player_id: Optional[str] = None) -> Game:
        """Create a new word ladder game.
        
        Args:
            difficulty: Difficulty level of the game
            game_mode: Game mode
            word_length: Length of words (4 or 5)
            player_id: Optional player ID
            
        Returns:
            Game instance with guaranteed solvable word pair
        """
        max_attempts = 20  # Increased attempts for better selection
        path = None
        start_word = None
        target_word = None
        
        logger.info(f"Creating game: difficulty={difficulty.value}, mode={game_mode.value}, length={word_length}")
        
        for attempt in range(max_attempts):
            # Get random word pair based on difficulty, mode, and length
            start_word, target_word = get_word_pair(
                length=word_length,
                difficulty=difficulty.value,  # Convert enum to string
                game_mode=game_mode.value     # Convert enum to string
            )
            
            logger.info(f"Attempt {attempt + 1}: Testing pair {start_word} -> {target_word}")
            
            # Verify that both words are valid
            if not self.word_validator.is_valid_word(start_word):
                logger.warning(f"Start word '{start_word}' is not valid")
                continue
                
            if not self.word_validator.is_valid_word(target_word):
                logger.warning(f"Target word '{target_word}' is not valid")
                continue
            
            # Check if there's a valid path between the words
            path = self.path_finder._find_path(start_word.upper(), target_word.upper())
            
            if path is not None and len(path) > 1:
                # Valid path found, create the game
                logger.info(f"Valid path found: {' -> '.join(path)}")
                break
            else:
                logger.warning(f"No valid path found for {start_word} -> {target_word}")
                
        if path is None or len(path) <= 1:
            # If no valid path found after all attempts, use guaranteed solvable pairs
            logger.warning("Using fallback guaranteed solvable pair")
            if word_length == 4:
                start_word, target_word = "COLD", "WARM"
            else:
                start_word, target_word = "HOUSE", "RANCH"
                
            # Verify the fallback path
            path = self.path_finder._find_path(start_word, target_word)
            if path is None:
                logger.error(f"Even fallback pair {start_word} -> {target_word} has no path!")
        
        # Create a new game instance
        game_id = str(uuid.uuid4())
        
        game = Game(
            id=game_id,
            start_word=start_word.upper(),  # Ensure uppercase
            target_word=target_word.upper(),  # Ensure uppercase
            current_word=start_word.upper(),
            moves=[],
            status=GameStatus.IN_PROGRESS.value,  # Use enum value
            difficulty=difficulty,
            game_mode=game_mode,
            player_id=player_id,
            created_at=datetime.now(),
            time_elapsed=0
        )
        
        logger.info(f"Game created: {game.start_word} -> {game.target_word}")
        return game
    
    def make_move(self, game: Game, word: str) -> MoveResult:
        """Make a move in the game by submitting a new word.
        
        Args:
            game: The current game instance
            word: The new word to move to
            
        Returns:
            MoveResult with the outcome of the move
            
        Raises:
            ValueError: If the move is invalid
        """
        word = word.upper()  # Ensure uppercase
        
        # Check if game is already completed
        if game.status != GameStatus.IN_PROGRESS.value:
            raise ValueError("Game is already completed")

        # Check time limit for TIMED mode
        if game.game_mode == GameMode.TIMED:
            time_elapsed = (datetime.now() - game.created_at).seconds
            if time_elapsed > 300:  # 5 minutes limit
                game.status = GameStatus.ABANDONED.value
                raise ValueError("Time limit exceeded")
            game.time_elapsed = time_elapsed
        
        # Validate the word
        if not self.word_validator.is_valid_word(word):
            raise ValueError(f"Invalid word: {word}")
            
        if not self.word_validator.is_one_letter_change(game.current_word, word):
            raise ValueError("Word must differ by exactly one letter")
        
        # Check if word was already used
        if word in game.moves or word == game.start_word:
            raise ValueError("Word already used in this game")
        
        # Update game state
        game.moves.append(word)
        game.current_word = word
        
        # Check if target reached
        is_target = (word == game.target_word)
        if is_target:
            game.status = GameStatus.COMPLETED.value
            message = f"Congratulations! You've reached the target word in {len(game.moves)} moves."
        else:
            # Check if we're still on a valid path
            remaining_path = self.path_finder._find_path(word, game.target_word)
            if remaining_path:
                moves_left = len(remaining_path) - 1
                message = f"Good move! Approximately {moves_left} moves remaining to reach the target."
            else:
                message = "Valid move, but this might not be the optimal path. Keep going!"
        
        # Update time elapsed for timed games
        if game.game_mode == GameMode.TIMED:
            game.time_elapsed = (datetime.now() - game.created_at).seconds
        
        # Create result
        result = MoveResult(
            is_target=is_target,
            moves_count=len(game.moves),
            path=game.moves.copy(),  # Copy to prevent mutation
            message=message
        )
        
        return result
    
    def get_hint(self, game: Game, hint_level: int = 1) -> Hint:
        """Get a hint for the current game state.
        
        Args:
            game: The current game instance
            hint_level: The level of hint to provide (1-3, with 3 being most revealing)
            
        Returns:
            A Hint object with hint information
        """
        # Check if game is already completed
        if game.status != GameStatus.IN_PROGRESS.value:
            return Hint(
                hint_type=HintType.GENERAL,
                hint_text="Game is already completed!"
            )
        
        # Find the optimal path to the target
        path = self.path_finder._find_path(game.current_word.upper(), game.target_word.upper())
        
        if not path or len(path) < 2:
            # If no path found or already at target, give general encouragement
            possible_words = self.word_validator.get_possible_words(game.current_word)
            if possible_words:
                return Hint(
                    hint_type=HintType.GENERAL,
                    hint_text=f"You can change one letter to make: {', '.join(possible_words[:3])}... Keep exploring!"
                )
            else:
                return Hint(
                    hint_type=HintType.GENERAL,
                    hint_text="Keep trying! Look for valid words by changing one letter."
                )
        
        # Get the next word in the optimal path
        next_word = path[1].upper()
        
        # Determine what kind of hint to give based on hint level
        if hint_level == 1:
            # General hint - give a semantic clue or general direction
            moves_left = len(path) - 1
            return Hint(
                hint_type=HintType.SEMANTIC,
                hint_text=f"You're approximately {moves_left} moves away from '{game.target_word}'. Think of words related to your target!"
            )
            
        elif hint_level == 2:
            # Position hint - tell which position to change
            position = None
            for i in range(len(game.current_word)):
                if game.current_word[i] != next_word[i]:
                    position = i
                    break
            
            if position is not None:
                return Hint(
                    hint_type=HintType.POSITION,
                    hint_text=f"Try changing the letter at position {position + 1} (the '{game.current_word[position]}').",
                    position=position
                )
            else:
                return Hint(
                    hint_type=HintType.GENERAL,
                    hint_text="Something went wrong with the hint. Keep trying!"
                )
            
        else:  # hint_level == 3
            # Letter hint - tell which letter to change and what to change it to
            position = None
            suggested_letter = None
            for i in range(len(game.current_word)):
                if game.current_word[i] != next_word[i]:
                    position = i
                    suggested_letter = next_word[i]
                    break
            
            if position is not None and suggested_letter is not None:
                return Hint(
                    hint_type=HintType.LETTER,
                    hint_text=f"Change the '{game.current_word[position]}' at position {position + 1} to '{suggested_letter}' to make '{next_word}'.",
                    position=position,
                    suggested_letter=suggested_letter
                )
            else:
                return Hint(
                    hint_type=HintType.GENERAL,
                    hint_text="You're very close! Keep trying with small changes."
                )
    
    def get_daily_challenge(self) -> Dict[str, Any]:
        """Get the daily challenge puzzle.
        
        Returns:
            A dictionary with the daily challenge information
        """
        today = datetime.now().date()
        
        # Use the date as a seed for random selection to ensure the same challenge all day
        random.seed(f"{today.year}{today.month:02d}{today.day:02d}")
        
        # Use guaranteed solvable pairs for daily challenges
        daily_pairs_4 = [
            ("COLD", "WARM"),
            ("BANK", "LOAN"), 
            ("FAST", "SLOW"),
            ("ROCK", "SAND"),
            ("LEAD", "GOLD")
        ]
        
        daily_pairs_5 = [
            ("HOUSE", "RANCH"),
            ("HAPPY", "SMILE"),
            ("MOUSE", "TIGER"),
            ("BRAIN", "THINK"),
            ("POWER", "LIGHT")
        ]
        
        # Alternate between 4 and 5 letter words based on day
        if today.day % 2 == 0:
            word_length = 4
            start_word, target_word = random.choice(daily_pairs_4)
        else:
            word_length = 5
            start_word, target_word = random.choice(daily_pairs_5)
        
        # Verify the path exists (should always be true for our guaranteed pairs)
        path = self.path_finder._find_path(start_word, target_word)
        if path:
            optimal_moves = len(path) - 1
        else:
            optimal_moves = 6  # Fallback estimate
        
        return {
            "date": today.isoformat(),
            "start_word": start_word.upper(),
            "target_word": target_word.upper(),
            "word_length": word_length,
            "difficulty": DifficultyLevel.MEDIUM.value,
            "optimal_moves": optimal_moves,
            "theme": "Daily Challenge"
        }
    
    def validate_game_state(self, game: Game) -> bool:
        """Validate that the current game state is consistent.
        
        Args:
            game: The game to validate
            
        Returns:
            True if game state is valid
        """
        # Check that start and target words are valid
        if not self.word_validator.is_valid_word(game.start_word):
            return False
            
        if not self.word_validator.is_valid_word(game.target_word):
            return False
        
        # Check that current word is valid
        if not self.word_validator.is_valid_word(game.current_word):
            return False
        
        # Check that moves form a valid chain
        current_check = game.start_word
        for move in game.moves:
            if not self.word_validator.is_one_letter_change(current_check, move):
                return False
            current_check = move
        
        return True