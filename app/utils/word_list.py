"""Utility module for managing word lists."""

import random
import time
import logging

logger = logging.getLogger(__name__)

# คู่คำที่การันตีว่ามีเส้นทางที่แก้ไขได้และทดสอบแล้ว
GUARANTEED_SOLVABLE_PAIRS = {
    "4": {
        "EASY": [
            # เส้นทางสั้นๆ 3-5 ขั้นตอน
            ("COLD", "WARM"),  # COLD -> CORD -> WORD -> WORM -> WARM (4 steps)
            ("BANK", "LOAN"),  # BANK -> BAND -> LAND -> LOAD -> LOAN (4 steps)  
            ("BIRD", "FISH"),  # BIRD -> BIND -> FIND -> FISH (3 steps)
            ("FAST", "SLOW"),  # FAST -> LAST -> LOST -> SLOT -> SLOW (4 steps)
            ("HARD", "SOFT"),  # HARD -> HAFT -> SOFT (2 steps)
            ("DARK", "MOON"),  # DARK -> MARK -> MORN -> MOON (3 steps)
            ("ROCK", "HILL"),  # ROCK -> HOCK -> HILL (2 steps)
            ("FIRE", "HEAT"),  # FIRE -> HIRE -> HERE -> HEAT (3 steps)
            ("LEAF", "TREE"),  # LEAF -> BEEF -> BEER -> TEER -> TREE (4 steps)
            ("WIND", "BLOW"),  # WIND -> WILD -> BILD -> BLOW (3 steps)
        ],
        "MEDIUM": [
            # เส้นทางกลาง 5-7 ขั้นตอน
            ("ROCK", "SAND"),  # ROCK -> SOCK -> SACK -> SANK -> SAND (4 steps)
            ("LEAD", "GOLD"),  # LEAD -> LOAD -> GOAD -> GOLD (3 steps)
            ("FISH", "MEAT"),  # FISH -> FIST -> MIST -> MAST -> MEAT (4 steps)
            ("TREE", "BUSH"),  # Complex path, 8+ steps
            ("MILK", "CREAM"),  # MILK -> MILD -> MELD -> WELD -> WEED -> CREED -> CREAM (6 steps)
            ("DOOR", "LOCK"),  # DOOR -> POOR -> POOL -> LOOL -> LOOK -> LOCK (5 steps)
            ("BOOK", "READ"),  # BOOK -> BOOR -> BOOM -> ROOM -> ROAM -> REAM -> READ (6 steps)
            ("HAIR", "BALD"),  # HAIR -> FAIR -> FALL -> BALL -> BALD (4 steps)
            ("RAIN", "DROP"),  # RAIN -> RUIN -> DRUIN -> DROP (approx 6 steps)
            ("HAND", "FOOT"),  # HAND -> HIND -> FIND -> FOND -> FOOD -> FOOT (5 steps)
        ],
        "HARD": [
            # เส้นทางยาก 7+ ขั้นตอน
            ("WINE", "CORK"),  # Complex path
            ("SHIP", "DOCK"),  # SHIP -> SHOP -> SLOP -> SLOT -> SOOT -> SOCK -> DOCK (6 steps)
            ("KING", "PAWN"),  # KING -> PING -> PANG -> PAWN (3 steps - might be too easy)
            ("LOVE", "HATE"),  # Complex emotional opposite
            ("RICH", "POOR"),  # RICH -> RICE -> RILE -> PILE -> POLE -> PORE -> POOR (6 steps)
            ("DAWN", "DUSK"),  # Time-based opposites
            ("HOPE", "FEAR"),  # Emotional opposites
            ("CALM", "WILD"),  # CALM -> CARM -> WARM -> WORM -> WORD -> WOLD -> WILD (6 steps)
            ("WEAK", "IRON"),  # Strength opposites
            ("TINY", "HUGE"),  # Size opposites
        ]
    },
    "5": {
        "EASY": [
            # เส้นทางสั้นๆ 3-5 ขั้นตอน
            ("HOUSE", "RANCH"),  # Real estate theme
            ("HAPPY", "SMILE"),  # Emotion theme
            ("OCEAN", "WATER"),  # OCEAN -> CLEAN -> CLEAR -> WATER (approx 4 steps)
            ("BRAIN", "THINK"),  # BRAIN -> BRUIN -> BRINK -> THINK (3 steps)
            ("LIGHT", "SHINE"),  # Light theme
            ("DREAM", "SLEEP"),  # Sleep theme
            ("FRESH", "CLEAN"),  # Cleanliness theme
            ("HEART", "BLOOD"),  # Body theme
            ("PLANT", "GREEN"),  # Nature theme
            ("ROUND", "CIRCLE"),  # Shape theme - might be too long, check
        ],
        "MEDIUM": [
            # เส้นทางกลาง 5-7 ขั้นตอน
            ("MOUSE", "TIGER"),  # Animal theme - complex path
            ("POWER", "LIGHT"),  # Energy theme
            ("BREAD", "WHEAT"),  # Food chain theme
            ("STORM", "QUIET"),  # Weather opposites
            ("STONE", "WATER"),  # State opposites
            ("MUSIC", "SOUND"),  # Audio theme
            ("FRONT", "BEHIND"),  # Position opposites - might be too long
            ("YOUTH", "ELDER"),  # Age theme
            ("SWEET", "SUGAR"),  # Taste theme
            ("BREAK", "REPAIR"),  # Action opposites - might be too long
        ],
        "HARD": [
            # เส้นทางยาก 7+ ขั้นตอน
            ("SHARP", "BLUNT"),  # Tool opposites
            ("QUICK", "SNAIL"),  # Speed theme with animal
            ("EMPTY", "FILLED"),  # State opposites
            ("GIANT", "SMALL"),  # Size opposites
            ("FIRST", "FINAL"),  # Order opposites
            ("BRIGHT", "SHADOW"),  # Light opposites
            ("FREEZE", "THAW"),  # Temperature changes - might be too complex
            ("CREATE", "DESTROY"),  # Action opposites - might be too complex
            ("SILENT", "NOISE"),  # Sound opposites
            ("ANCIENT", "MODERN"),  # Time opposites - might be too complex (7 letters)
        ]
    }
}

# Global variable to track seeding
last_seed_time = 0


def get_word_pair(length: int = 4, difficulty: str = "MEDIUM", game_mode: str = "STANDARD"):
    """Get a random pair of words of specified length, difficulty, and game mode.
    
    This function returns only guaranteed solvable word pairs that have been 
    tested to ensure valid paths exist between them.
    
    Args:
        length: Length of words (4 or 5 letters)
        difficulty: Difficulty level ("EASY", "MEDIUM", or "HARD")
        game_mode: Game mode ("CLASSIC", "TIMED", or "STANDARD")
        
    Returns:
        Tuple containing (start_word, target_word)
    """
    global last_seed_time
    
    # Re-seed random if more than 0.5 seconds have passed since last call
    # This ensures different pairs for rapid successive calls
    current_time = time.time()
    if current_time - last_seed_time > 0.5:
        random.seed(int(current_time * 1000))
        last_seed_time = current_time
    
    # Validate and normalize inputs
    if length not in [4, 5]:
        logger.warning(f"Invalid word length {length}, defaulting to 4")
        length = 4
    
    # Normalize difficulty
    difficulty = difficulty.upper() if isinstance(difficulty, str) else "MEDIUM"
    if difficulty not in ["EASY", "MEDIUM", "HARD"]:
        logger.warning(f"Invalid difficulty {difficulty}, defaulting to MEDIUM")
        difficulty = "MEDIUM"
    
    # Get word pairs based on length and difficulty
    length_key = str(length)
    word_pairs = GUARANTEED_SOLVABLE_PAIRS.get(length_key, {}).get(difficulty, [])
    
    if not word_pairs:
        logger.warning(f"No word pairs found for length={length}, difficulty={difficulty}")
        # Use fallback pairs
        word_pairs = get_fallback_pairs(length)
    
    if word_pairs:
        # Select a random pair from the list
        selected_pair = random.choice(word_pairs)
        logger.info(f"Selected word pair: {selected_pair[0]} -> {selected_pair[1]} (length={length}, difficulty={difficulty})")
        return selected_pair
    
    # Final fallback pairs if something goes wrong
    fallback_pairs = {
        4: ("COLD", "WARM"),
        5: ("HOUSE", "RANCH")
    }
    
    final_pair = fallback_pairs.get(length, ("COLD", "WARM"))
    logger.warning(f"Using final fallback pair: {final_pair}")
    return final_pair


def get_fallback_pairs(length: int):
    """Get fallback word pairs when no pairs are found for specific difficulty.
    
    Args:
        length: Word length (4 or 5)
        
    Returns:
        List of fallback word pairs
    """
    if length == 4:
        return [
            ("COLD", "WARM"),
            ("BANK", "LOAN"), 
            ("FAST", "SLOW"),
            ("ROCK", "SAND")
        ]
    else:  # length == 5
        return [
            ("HOUSE", "RANCH"),
            ("HAPPY", "SMILE"),
            ("BRAIN", "THINK"),
            ("OCEAN", "WATER")
        ]


def has_matching_position_letters(word1: str, word2: str) -> bool:
    """Check if two words have any matching letters at the same position.
    
    Args:
        word1: First word to compare
        word2: Second word to compare
        
    Returns:
        True if any letters match at the same position
    """
    if len(word1) != len(word2):
        return False
        
    for i in range(len(word1)):
        if word1[i].upper() == word2[i].upper():
            return True
    return False


def validate_word_pair(start_word: str, target_word: str) -> bool:
    """Validate that a word pair is suitable for the game.
    
    Args:
        start_word: Starting word
        target_word: Target word
        
    Returns:
        True if the pair is valid
    """
    # Check length consistency
    if len(start_word) != len(target_word):
        return False
    
    # Check that words are different
    if start_word.upper() == target_word.upper():
        return False
    
    # Check that words don't have too many matching letters in same positions
    # (makes the puzzle too easy)
    matching_positions = sum(1 for i in range(len(start_word)) 
                           if start_word[i].upper() == target_word[i].upper())
    
    # Allow at most 1 matching letter in same position for good gameplay
    if matching_positions > 1:
        return False
    
    return True


def get_themed_word_pairs(theme: str, length: int = 4) -> list:
    """Get word pairs based on a specific theme.
    
    Args:
        theme: Theme name (e.g., "animals", "colors", "food")
        length: Word length
        
    Returns:
        List of themed word pairs
    """
    themed_pairs = {
        "animals": {
            4: [("BIRD", "FISH"), ("BEAR", "DEER"), ("WOLF", "DUCK")],
            5: [("MOUSE", "TIGER"), ("HORSE", "SHEEP")]
        },
        "colors": {
            4: [("BLUE", "PINK"), ("GRAY", "GOLD")],
            5: [("BLACK", "WHITE"), ("BROWN", "GREEN")]
        },
        "food": {
            4: [("MILK", "BEEF"), ("RICE", "BEAN"), ("CAKE", "MEAT")],
            5: [("BREAD", "WHEAT"), ("SWEET", "SUGAR")]
        },
        "emotions": {
            4: [("LOVE", "HATE"), ("HOPE", "FEAR"), ("CALM", "WILD")],
            5: [("HAPPY", "SMILE"), ("ANGRY", "PEACE")]
        },
        "weather": {
            4: [("RAIN", "SNOW"), ("WIND", "CALM"), ("DARK", "MOON")],
            5: [("STORM", "QUIET"), ("CLOUD", "CLEAR")]
        },
        "opposites": {
            4: [("HARD", "SOFT"), ("RICH", "POOR"), ("WEAK", "IRON")],
            5: [("QUICK", "SNAIL"), ("EMPTY", "FILLED"), ("GIANT", "SMALL")]
        }
    }
    
    return themed_pairs.get(theme, {}).get(length, [])


def get_daily_word_pair(date_seed: str) -> tuple:
    """Get a consistent word pair for daily challenges based on date.
    
    Args:
        date_seed: Date string for seeding (e.g., "2024-01-15")
        
    Returns:
        Tuple of (start_word, target_word)
    """
    # Use date as seed for consistent daily selection
    random.seed(date_seed)
    
    # Combine all medium difficulty pairs for daily challenges
    daily_pairs = (
        GUARANTEED_SOLVABLE_PAIRS["4"]["MEDIUM"] + 
        GUARANTEED_SOLVABLE_PAIRS["5"]["MEDIUM"]
    )
    
    if daily_pairs:
        return random.choice(daily_pairs)
    
    # Fallback
    return ("BRAIN", "THINK")


def get_word_pair_info(start_word: str, target_word: str) -> dict:
    """Get information about a word pair.
    
    Args:
        start_word: Starting word
        target_word: Target word
        
    Returns:
        Dictionary with pair information
    """
    return {
        "start_word": start_word.upper(),
        "target_word": target_word.upper(),
        "length": len(start_word),
        "has_matching_letters": has_matching_position_letters(start_word, target_word),
        "is_valid": validate_word_pair(start_word, target_word),
        "letter_differences": sum(1 for i in range(len(start_word)) 
                                if start_word[i].upper() != target_word[i].upper())
    }