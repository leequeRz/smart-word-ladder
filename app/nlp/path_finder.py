"""Path Finder module for Smart Word Ladder.

This module contains functionality for finding paths between words and determining optimal moves.
"""

from typing import List, Optional, Dict, Set
from collections import deque
from app.core.word_validator import WordValidator
import logging

logger = logging.getLogger(__name__)


class PathFinder:
    """Class for finding word paths in the Smart Word Ladder game.
    
    This class handles path finding between words and determining optimal next moves.
    """
    
    def __init__(self):
        """Initialize the path finder with required components."""
        self.word_validator = WordValidator()
        self.path_cache: Dict[str, Dict[str, List[str]]] = {}
        self.max_search_depth = 15  # Prevent infinite searches
    
    def path_exists(self, start_word: str, target_word: str) -> bool:
        """Check if a path exists between two words.
        
        Args:
            start_word: The starting word
            target_word: The target word
            
        Returns:
            True if a path exists, False otherwise
        """
        # Normalize inputs
        start_word = start_word.upper()
        target_word = target_word.upper()
        
        # Use cached path if available
        cache_key = f"{start_word}_{target_word}"
        if cache_key in self.path_cache:
            return True
            
        # Find path using breadth-first search
        path = self._find_path(start_word, target_word)
        return path is not None and len(path) > 1
    
    def get_next_word(self, current_word: str, target_word: str) -> str:
        """Get the optimal next word in the path to the target.
        
        Args:
            current_word: The current word
            target_word: The target word
            
        Returns:
            The next word in the optimal path, or target_word if no path found
        """
        # Normalize inputs
        current_word = current_word.upper()
        target_word = target_word.upper()
        
        # Check cache first
        cache_key = f"{current_word}_{target_word}"
        if cache_key in self.path_cache:
            path = self.path_cache[cache_key]
            return path[1] if len(path) > 1 else target_word
            
        # Find new path
        path = self._find_path(current_word, target_word)
        if path and len(path) > 1:
            return path[1]
            
        return target_word
    
    def _find_path(self, start_word: str, target_word: str) -> Optional[List[str]]:
        """Find a path between two words using breadth-first search.
        
        Args:
            start_word: The starting word (will be normalized to uppercase)
            target_word: The target word (will be normalized to uppercase)
            
        Returns:
            List of words forming the path, or None if no path exists
        """
        # Normalize to uppercase for consistency with WordValidator
        start_word = start_word.upper()
        target_word = target_word.upper()
        
        logger.info(f"Finding path from {start_word} to {target_word}")
        
        # Return immediately if words are the same
        if start_word == target_word:
            return [start_word]
        
        # Check if both words are valid
        if not self.word_validator.is_valid_word(start_word):
            logger.warning(f"Start word '{start_word}' is not valid")
            return None
            
        if not self.word_validator.is_valid_word(target_word):
            logger.warning(f"Target word '{target_word}' is not valid")
            return None
            
        # Initialize BFS
        queue = deque([(start_word, [start_word])])
        visited: Set[str] = {start_word}
        depth = 0
        
        while queue and depth < self.max_search_depth:
            # Process all nodes at current depth
            next_queue = deque()
            
            while queue:
                current_word, path = queue.popleft()
                
                # Get all possible next words (these are returned in uppercase)
                next_words = self.word_validator.get_possible_words(current_word)
                
                for next_word in next_words:
                    next_word = next_word.upper()  # Ensure uppercase
                    
                    if next_word not in visited:
                        visited.add(next_word)
                        new_path = path + [next_word]
                        
                        # Check if we've reached the target
                        if next_word == target_word:
                            # Cache the path for future use
                            cache_key = f"{start_word}_{target_word}"
                            self.path_cache[cache_key] = new_path
                            
                            logger.info(f"Found path: {' -> '.join(new_path)}")
                            return new_path
                            
                        next_queue.append((next_word, new_path))
            
            queue = next_queue
            depth += 1
        
        logger.warning(f"No path found from {start_word} to {target_word} within depth {self.max_search_depth}")
        return None
    
    def get_shortest_path(self, start_word: str, target_word: str) -> Optional[List[str]]:
        """Get the shortest path between two words.
        
        This is an alias for _find_path since BFS naturally finds the shortest path.
        
        Args:
            start_word: The starting word
            target_word: The target word
            
        Returns:
            List of words forming the shortest path, or None if no path exists
        """
        return self._find_path(start_word, target_word)
    
    def get_all_paths(self, start_word: str, target_word: str, max_paths: int = 5) -> List[List[str]]:
        """Find multiple possible paths between two words.
        
        This is used for the Word Web game mode where players can see multiple solutions.
        
        Args:
            start_word: The starting word
            target_word: The target word
            max_paths: Maximum number of paths to return
            
        Returns:
            List of paths, where each path is a list of words
        """
        start_word = start_word.upper()
        target_word = target_word.upper()
        
        paths: List[List[str]] = []
        
        # First, get the shortest path
        shortest_path = self._find_path(start_word, target_word)
        if shortest_path:
            paths.append(shortest_path)
            
        # If we want more paths, we could implement a more complex algorithm
        # For now, return just the shortest path
        return paths
    
    def clear_cache(self):
        """Clear the path cache."""
        self.path_cache.clear()
        logger.info("Path cache cleared")
    
    def get_cache_size(self) -> int:
        """Get the current size of the path cache."""
        return len(self.path_cache)