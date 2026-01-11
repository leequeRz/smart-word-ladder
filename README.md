# Smart Word Ladder

A modern take on the classic Word Ladder game created by Lewis Carroll, enhanced with NLP technology.

## Overview

Smart Word Ladder is a word game where players must transform a starting word into a target word by changing one letter at a time, with each intermediate step being a valid English word. The game features intelligent hints, difficulty levels, and various game modes.

## Features

- **Core Gameplay**: Transform words one letter at a time
- **Automatic Word Validation**: NLP-powered verification of word validity
- **Difficulty Levels**: From easy (short/common words) to hard (long/rare words)
- **Intelligent Hint System**: Using word embeddings to provide contextual hints
- **Daily Challenges**: New puzzles every day (similar to Wordle)
- **Timed Mode**: Race against the clock to find the shortest path

## Additional Game Modes

- **Word Web**: Multiple possible paths between words
- **Time Attack**: Create as many paths as possible within a time limit
- **Thematic Challenges**: Word puzzles in specific categories
- **Multiplayer**: Compete with others for the shortest or fastest path

## Technology

Built with Python using modern NLP techniques including:
- Word embeddings (Word2Vec, GloVe, BERT)
- WordNet integration
- Custom dictionaries and word frequency analysis
- Path-finding algorithms

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-word-ladder.git
cd smart-word-ladder

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main

# Test Result on Local
http://localhost:8000
```

## License

MIT
