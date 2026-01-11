"""Word Processor module for Smart Word Ladder.

This module contains functionality for processing words semantically and generating hints.
"""

import random
from typing import List, Dict, Any, Optional
import nltk
from nltk.corpus import wordnet
import numpy as np

# Try to import gensim for word embeddings
try:
    from gensim.models import KeyedVectors
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False

# Try to import transformers for BERT embeddings
try:
    from transformers import BertTokenizer, BertModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Download required NLTK data if not already present
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class WordProcessor:
    """Class for processing words semantically in the Smart Word Ladder game.
    
    This class handles word embeddings, semantic similarity, and hint generation.
    """
    
    def __init__(self):
        """Initialize the word processor with available NLP models."""
        self.word2vec_model = None
        self.bert_model = None
        self.bert_tokenizer = None
        
        # Load word embeddings if available
        self._load_word_embeddings()
    
    def _load_word_embeddings(self):
        """Load word embedding models if available.
        
        This tries to load Word2Vec and/or BERT models based on availability.
        """
        # Try to load Word2Vec model
        if GENSIM_AVAILABLE:
            try:
                # In a real implementation, you would download or load a pre-trained model
                # For now, we'll just note that it would be loaded here
                # self.word2vec_model = KeyedVectors.load_word2vec_format('path/to/model', binary=True)
                pass
            except Exception as e:
                print(f"Could not load Word2Vec model: {e}")
        
        # Try to load BERT model
        if TRANSFORMERS_AVAILABLE:
            try:
                # In a real implementation, you would load the BERT model here
                # self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
                # self.bert_model = BertModel.from_pretrained('bert-base-uncased')
                pass
            except Exception as e:
                print(f"Could not load BERT model: {e}")
    
    def get_word_embedding(self, word: str) -> Optional[np.ndarray]:
        """Get the embedding vector for a word.
        
        Args:
            word: The word to get an embedding for
            
        Returns:
            Numpy array with the word embedding, or None if not available
        """
        word = word.lower()
        
        # Try Word2Vec first if available
        if self.word2vec_model is not None and word in self.word2vec_model:
            return self.word2vec_model[word]
        
        # Try BERT if available
        if self.bert_model is not None and self.bert_tokenizer is not None:
            # This would be implemented with actual BERT embedding extraction
            # For now, return None
            return None
        
        return None
    
    def get_semantic_similarity(self, word1: str, word2: str) -> float:
        """Calculate semantic similarity between two words.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Similarity score between 0 and 1
        """
        # Get embeddings
        embedding1 = self.get_word_embedding(word1)
        embedding2 = self.get_word_embedding(word2)
        
        # If we have both embeddings, calculate cosine similarity
        if embedding1 is not None and embedding2 is not None:
            # Cosine similarity
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(similarity)
        
        # Fall back to WordNet similarity if embeddings not available
        return self._get_wordnet_similarity(word1, word2)
    
    def _get_wordnet_similarity(self, word1: str, word2: str) -> float:
        """Calculate semantic similarity using WordNet.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Similarity score between 0 and 1
        """
        # Get WordNet synsets
        synsets1 = wordnet.synsets(word1)
        synsets2 = wordnet.synsets(word2)
        
        if not synsets1 or not synsets2:
            return 0.0
        
        # Calculate max similarity between any synset pair
        max_similarity = 0.0
        
        for synset1 in synsets1:
            for synset2 in synsets2:
                try:
                    similarity = synset1.path_similarity(synset2) or 0.0
                    max_similarity = max(max_similarity, similarity)
                except:
                    continue
        
        return max_similarity
    
    def get_semantic_hint(self, target_word: str) -> str:
        """Generate a semantic hint for the target word.
        
        Args:
            target_word: The word to generate a hint for
            
        Returns:
            A hint string related to the word's meaning
        """
        # Get WordNet synsets for the word
        synsets = wordnet.synsets(target_word)
        
        if not synsets:
            # Fallback for words not in WordNet
            return f"Think of a {len(target_word)}-letter word that might be relevant."
        
        # Get the first synset (most common meaning)
        synset = synsets[0]
        
        # Get definition and examples
        definition = synset.definition()
        examples = synset.examples()
        
        # Generate hint based on available information
        if examples and random.random() < 0.5:
            # Use an example sentence with the word replaced by blanks
            example = examples[0]
            hint_text = example.replace(target_word, "_____")
            return f"Think of a word that fits in this context: '{hint_text}'"
        else:
            # Use the definition
            return f"Think of a {len(target_word)}-letter word that means: '{definition}'"
    
    def get_related_words(self, word: str, n: int = 5) -> List[str]:
        """Get semantically related words.
        
        Args:
            word: The source word
            n: Number of related words to return
            
        Returns:
            List of related words
        """
        # If we have word embeddings, use them to find similar words
        if self.word2vec_model is not None:
            try:
                similar_words = [w for w, _ in self.word2vec_model.most_similar(word, topn=n)]
                return similar_words
            except:
                pass
        
        # Fall back to WordNet
        related = []
        synsets = wordnet.synsets(word)
        
        if not synsets:
            return related
        
        # Get synonyms
        for synset in synsets:
            for lemma in synset.lemmas():
                related.append(lemma.name())
                
                # Get antonyms
                for antonym in lemma.antonyms():
                    related.append(antonym.name())
        
        # Remove duplicates and the original word
        related = list(set([w for w in related if w != word]))
        
        # Return at most n words
        return related[:n]