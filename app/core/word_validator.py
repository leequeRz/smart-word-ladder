"""Word Validator module for Smart Word Ladder.

This module contains functionality for validating words in the game.
Enhanced to use NLTK WordNet and filter out uncommon/foreign words.
"""

import re
import nltk
from nltk.corpus import wordnet, words
from typing import Set, List, Dict, Optional
import logging

# Download required NLTK data if not already present
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

logger = logging.getLogger(__name__)


class WordValidator:
    """Class for validating words in the Smart Word Ladder game.
    
    This class handles word validation using both NLTK WordNet and custom dictionaries.
    It also filters out uncommon, foreign, or technical words to ensure good gameplay.
    """
    
    def __init__(self, min_word_length: int = 3, max_word_length: int = 8):
        """Initialize the word validator with custom dictionaries and NLTK.
        
        Args:
            min_word_length: Minimum length of valid words
            max_word_length: Maximum length of valid words
        """
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        self.custom_words: Set[str] = set()
        self._wordnet_cache: Dict[str, bool] = {}
        self._nltk_words_cache: Optional[Set[str]] = None
        self._filtered_words_cache: Dict[int, Set[str]] = {}
        
        # Words to exclude (foreign words, proper nouns, technical terms, etc.)
        self._excluded_words = {
            # Foreign/ethnic terms that might confuse players
            "YURTA", "YURT", "MASAI", "MAASAI", "HINDI", "URDU", "BANTU",
            "ZULU", "SWAZI", "TAMIL", "TELUGU", "SCOTS", "WELSH", "GAELIC",
            
            # Technical/scientific terms
            "BENZO", "NITRO", "HYDRO", "THIOL", "HEXYL", "BUTYL", "ETHYL",
            "PHENYL", "VINYL", "OXIME", "AZIDE", "OXIDE", "ESTER",
            
            # Abbreviations and acronyms
            "RADAR", "SONAR", "LASER", "SCUBA", "AWASH", "SWATH",
            
            # Very uncommon English words
            "QUAFF", "QUASH", "QUALM", "QUARK", "QUASI", "QUASAR",
            "FJORD", "SHARD", "WHARF", "SCARF", "DWARF",
            
            # Words with unusual letter patterns
            "GYOZA", "PIZZA", "FUZZY", "JAZZY", "DIZZY", "FIZZY"
        }
        
        # Load custom dictionary words (keeping existing words for compatibility)
        self._load_custom_dictionary()
        
        # Load NLTK words corpus
        self._load_nltk_words()
        
        # Add critical path words for guaranteed solvable paths
        self._add_critical_path_words()
        
    def _add_critical_path_words(self):
        """Add critical words needed for guaranteed solvable paths."""
        critical_words = {
            # COLD -> WARM path - ต้องมีทุกคำ
            "COLD", "CORD", "WORD", "WORM", "WARM", "WOLD", "WILD", "WELD", "WEND", "WIND",
            "CARD", "WARD", "WARE", "WORE", "WORT", "COLT", "BOLT", "BOLE", "BORE", "BARE",
            
            # BANK -> LOAN path
            "BANK", "BAND", "LAND", "LOAD", "LOAN", "BUNK", "LANK", "LEAN", "BALD", "BOLD",
            
            # BIRD -> FISH path
            "BIRD", "BIND", "FIND", "FISH", "FIST", "BARD", "BEAD", "BEAT", "BEND", "BEST",
            
            # FAST -> SLOW path  
            "FAST", "LAST", "LOST", "SLOT", "SLOW", "CAST", "COST", "COLT", "SCOT", "SHOT",
            
            # ROCK -> SAND path
            "ROCK", "SOCK", "SACK", "SANK", "SAND", "RACK", "ROOK", "RUCK", "RANK", "RANG",
            
            # LEAD -> GOLD path
            "LEAD", "LOAD", "GOAD", "GOLD", "GLAD", "GOOD", "ROAD", "READ",
            
            # TREE -> BUSH path (complex but necessary)
            "TREE", "FREE", "FLEE", "FLEW", "BLEW", "BLOW", "BROW", "CROW", "CRAW",
            "CRAM", "GRAM", "GRIM", "GRIT", "BRIT", "BRUT", "BUST", "BUSH", "GREW",
            
            # 5-letter critical words
            "HOUSE", "MOUSE", "MOOSE", "LOOSE", "LANCE", "RANCH", "HORDE", "HORSE", "WORSE",
            "HAPPY", "HARPY", "SHARP", "SHARE", "SHIRE", "SPIRE", "SMILE", "WHILE", "SHINE",
            "BRAIN", "BRUIN", "BRINK", "THINK", "THING", "BRING", "BLINK", "BLANK",
            "OCEAN", "CLEAN", "CLEAR", "CHEAR", "WHEAT", "WATER", "LATER", "CATER", "LASER",
            
            # Additional transition words that are commonly needed
            "BARE", "CARE", "DARE", "FARE", "HARE", "MARE", "PARE", "RARE", "TARE", "WARE",
            "BALE", "DALE", "GALE", "HALE", "KALE", "MALE", "PALE", "SALE", "TALE", "VALE",
            "BANE", "CANE", "DANE", "FANE", "JANE", "LANE", "MANE", "PANE", "SANE", "VANE",
            "BAKE", "CAKE", "FAKE", "JAKE", "LAKE", "MAKE", "RAKE", "SAKE", "TAKE", "WAKE",
            "BASE", "CASE", "EASE", "LASE", "VASE", "WISE", "ROSE", "POSE", "NOSE", "LOSE",
            
            # Common connecting words
            "ABLE", "MILE", "PILE", "TILE", "BILE", "FILE", "NILE", "WILE", "HOLE", "ROLE",
            "BONE", "CONE", "DONE", "GONE", "HONE", "LONE", "NONE", "TONE", "ZONE", "PONE",
            "BORE", "CORE", "FORE", "GORE", "LORE", "MORE", "PORE", "SORE", "TORE", "WORE",
            "BODE", "CODE", "LODE", "MODE", "NODE", "RODE", "RUDE", "NUDE", "DUDE", "TUBE",
            "BOLE", "COLE", "DOLE", "HOLE", "MOLE", "POLE", "ROLE", "SOLE", "TOLE", "VOLE",
            
            # Five letter connecting words - สำคัญมาก
            "BOARD", "HOARD", "SWORD", "WORLD", "WORTH", "NORTH", "FORTH", "MONTH", "SOUTH",
            "PLACE", "GRACE", "SPACE", "TRACE", "BRACE", "PEACE", "PIECE", "SLICE", "PRICE",
            "PLANE", "CRANE", "BRAIN", "GRAIN", "TRAIN", "STAIN", "CHAIN", "PLAIN", "SPAIN",
            "PLANT", "GRANT", "GIANT", "SLANT", "WANT", "PAINT", "SAINT", "FAINT", "POINT",
            "PLATE", "STATE", "SLATE", "GRATE", "CRATE", "SKATE", "STAKE", "SNAKE", "SHAKE",
            "PRICE", "SLICE", "SPICE", "TWICE", "VOICE", "CHOICE", "JUICE", "DANCE", "FENCE",
            "PRIDE", "BRIDE", "GUIDE", "SLIDE", "GLIDE", "ASIDE", "WIDE", "RIDE", "TIDE",
            "PRIME", "CRIME", "GRIME", "SLIME", "CHIME", "TIME", "DIME", "LIME", "MIME",
            
            # Words that help bridge different letters - เพิ่มเติมสำหรับเส้นทางซับซ้อน
            "BLEND", "BLIND", "BLOOD", "BLOOM", "BLOWN", "BOARD", "BOAST", "BOOST", "BREAD",
            "BREAK", "BREED", "BRING", "BROAD", "BROKE", "BROWN", "BUILD", "BUILT", "CHAIR",
            "CHAIN", "CHARM", "CHART", "CHASE", "CHEAP", "CHECK", "CHEST", "CHILD", "CHINA",
            "CLAIM", "CLASS", "CLEAN", "CLEAR", "CLIMB", "CLOCK", "CLOSE", "CLOUD", "COACH",
            "COAST", "COULD", "COUNT", "COURT", "COVER", "CRAFT", "CRASH", "CREAM", "CRIME",
            "CROSS", "CROWD", "CROWN", "DANCE", "DEATH", "DEPTH", "DOUBT", "DRAFT", "DRAMA",
            "DRAWN", "DREAM", "DRESS", "DRILL", "DRINK", "DRIVE", "DROVE", "EARLY", "EARTH",
            
            # Important bridge words for common patterns
            "THEIR", "THERE", "THESE", "THREE", "THREW", "THROW", "TIGHT", "TIMES", "TODAY",
            "TRADE", "TRAIN", "TREAT", "TREND", "TRIAL", "TRIED", "TRIES", "TRUCK", "TRULY",
            "TRUST", "TRUTH", "TWICE", "UNDER", "UNION", "UNITY", "UNTIL", "UPPER", "UPSET",
            "URBAN", "USAGE", "USUAL", "VALID", "VALUE", "VIDEO", "VIRUS", "VISIT", "VITAL",
            "VOICE", "WASTE", "WATCH", "WATER", "WHEEL", "WHERE", "WHICH", "WHILE", "WHITE",
            "WHOLE", "WHOSE", "WOMAN", "WOMEN", "WORLD", "WORRY", "WORSE", "WORST", "WORTH",
            "WOULD", "WOUND", "WRITE", "WRONG", "WROTE", "YIELD", "YOUNG", "YOUTH", "ZERO"
        }
        
        # Add all critical words to custom words (both cases)
        for word in critical_words:
            self.custom_words.add(word.lower())
            self.custom_words.add(word.upper())
            
        logger.info(f"Added {len(critical_words)} critical path words to validator")
        
    def _load_nltk_words(self):
        """Load NLTK words corpus for comprehensive validation."""
        try:
            nltk_words_raw = set(word.upper() for word in words.words())
            
            # Filter out unwanted words
            nltk_words_filtered = set()
            for word in nltk_words_raw:
                if self._is_good_english_word(word):
                    nltk_words_filtered.add(word)
            
            self._nltk_words_cache = nltk_words_filtered
            logger.info(f"Loaded {len(nltk_words_filtered)} filtered words from NLTK corpus")
        except Exception as e:
            logger.error(f"Failed to load NLTK words corpus: {e}")
            self._nltk_words_cache = set()
    
    def _is_good_english_word(self, word: str) -> bool:
        """Check if a word is a good common English word for the game.
        
        Args:
            word: Word to check
            
        Returns:
            True if word is suitable for the game
        """
        word = word.upper()
        
        # Skip excluded words
        if word in self._excluded_words:
            return False
        
        # Skip words with unusual characters or patterns
        if not re.match(r'^[A-Z]+$', word):
            return False
        
        # Skip very short or very long words for this check
        if len(word) < 3 or len(word) > 8:
            return False
        
        # Skip words with too many repeated letters (like ZZZZZ)
        if len(set(word)) < len(word) * 0.6:  # Less than 60% unique letters
            return False
        
        # Skip words with unusual letter frequencies
        unusual_letters = {'Q', 'X', 'Z', 'J'}
        unusual_count = sum(1 for letter in word if letter in unusual_letters)
        if unusual_count > 1:  # More than 1 unusual letter
            return False
        
        # Skip words that look like abbreviations (all consonants, etc.)
        vowels = {'A', 'E', 'I', 'O', 'U'}
        vowel_count = sum(1 for letter in word if letter in vowels)
        if vowel_count == 0 and len(word) > 2:  # No vowels in word longer than 2
            return False
        
        # Additional checks for very common words vs obscure ones
        # Prefer words with balanced vowel-consonant ratio
        consonant_count = len(word) - vowel_count
        if vowel_count > 0:
            ratio = consonant_count / vowel_count
            if ratio > 4 or ratio < 0.25:  # Very unbalanced
                return False
        
        return True
        
    def _load_custom_dictionary(self):
        """Load words from custom dictionaries."""
        # Common English words for 4 letters - curated list
        words_4 = [
            # Animals
            "bird", "fish", "bear", "deer", "duck", "goat", "wolf", "lion",
            
            # Basic words - very common only
            "cold", "warm", "hard", "soft", "dark", "life", "time", "work",
            "play", "game", "word", "book", "page", "door", "room", "wall",
            "hand", "head", "foot", "body", "hair", "face", "neck", "back",
            
            # Words needed for COLD->WARM path
            "cold", "cord", "word", "worm", "warm",
            "wold", "wild", "weld", "wend", "wind",
            "card", "ward", "ware", "wore", "wort",
            "colt", "bolt", "bole", "bore", "bare",
            
            # Very common English words only
            "able", "also", "area", "army", "away", "baby",
            "back", "ball", "band", "bank", "base", "bath", "beat",
            "been", "beer", "bell", "belt", "best", "bill", "blow",
            "blue", "boat", "body", "bomb", "bond", "bone", "book", "boot",
            "born", "boss", "both", "bowl", "burn", "bush", "busy",
            "cake", "call", "calm", "came", "camp", "care",
            "cart", "case", "cash", "cast", "cave", "cell", "city",
            "club", "coal", "coat", "code", "coin", "cold", "come",
            "cook", "cool", "copy", "core", "corn", "cost", "crew", "crop",
            "dark", "data", "date", "dawn", "dead", "deal", "dear",
            "deep", "desk", "died", "diet", "dirt",
            "dish", "dock", "door", "down", "draw", "drew", "drop",
            "drug", "drum", "duck", "dust", "duty", "each", "earn",
            "ease", "east", "easy", "edge", "else", "even", "ever", "exit",
            "face", "fact", "fail", "fair", "fall", "farm", "fast", "fate",
            "fear", "feed", "feel", "feet", "fell", "felt", "file", "fill",
            "film", "find", "fine", "fire", "firm", "fish", "five", "flag",
            "flat", "flow", "fold", "folk", "food", "foot", "form", "fort",
            "four", "free", "from", "fuel", "full", "fund", "gain", "game",
            "gate", "gave", "gear", "gift", "girl", "give", "glad",
            "goal", "gold", "golf", "gone", "good", "gray", "grew",
            "grow", "hair", "half", "hall", "hand", "hang", "hard",
            "harm", "hate", "have", "head", "hear", "heat", "held", "hell",
            "help", "here", "hero", "hide", "high", "hill", "hire", "hold",
            "hole", "holy", "home", "hope", "horn", "host", "hour", "huge",
            "hung", "hunt", "hurt", "idea", "inch", "into", "iron", "item",
            "join", "joke", "jump", "jury", "just", "keep",
            "kept", "kick", "kill", "kind", "king", "knee", "knew", "know",
            "lack", "lady", "laid", "lake", "lamp", "land", "lane", "last",
            "late", "lead", "leaf", "lean", "left", "lend", "less", "life", "lift",
            "like", "line", "link", "list", "live", "load", "loan", "lock",
            "long", "look", "lord", "lose", "loss", "lost", "loud",
            "love", "luck", "made", "mail", "main", "make", "male", "mall",
            "many", "mark", "mass", "mate", "meal", "mean", "meat", "meet",
            "menu", "mere", "mile", "milk", "mill", "mind", "mine",
            "mint", "miss", "mode", "mood", "moon", "more", "most", "move",
            "much", "must", "name", "navy", "near", "neck", "need", "news",
            "next", "nice", "nine", "none", "noon", "nose",
            "note", "okay", "once", "only", "onto", "open", "oral", "over",
            "pace", "pack", "page", "paid", "pain", "pair", "palm", "park", "part",
            "pass", "past", "path", "peak", "pick", "pink", "pipe", "plan",
            "play", "plot", "plug", "plus", "poem", "poet", "pole", "poll", "pond",
            "pool", "poor", "port", "post", "pull", "pure", "push", "quit",
            "race", "rail", "rain", "rank", "rare", "rate", "read", "real",
            "rear", "rely", "rent", "rest", "rice", "rich", "ride", "ring",
            "rise", "risk", "road", "rock", "role", "roll", "roof", "room", "root",
            "rope", "rose", "rule", "rush", "safe", "said", "sail",
            "sale", "salt", "same", "sand", "save", "seat", "seed", "seek",
            "seem", "seen", "self", "sell", "send", "sent", "ship", "shoe",
            "shop", "shot", "show", "shut", "sick", "side", "sign", "silk",
            "sing", "sink", "site", "size", "skin", "slip", "slow", "snow", "soft",
            "soil", "sold", "sole", "some", "song", "soon", "sort", "soul",
            "spot", "star", "stay", "step", "stop", "such", "suit", "sure",
            "swim", "tail", "take", "tale", "talk", "tall", "tank", "tape",
            "task", "team", "tell", "tend", "term", "test", "text",
            "than", "that", "them", "then", "they", "thin", "this", "thus",
            "tide", "tiny", "told", "toll", "tone", "took", "tool",
            "tour", "town", "tree", "trip", "true", "tune", "turn", "twin",
            "type", "unit", "upon", "used", "user", "vary", "vast", "very",
            "view", "vote", "wage", "wait", "wake", "walk", "wall",
            "want", "ward", "warm", "wash", "wave", "weak", "wear", "week",
            "well", "went", "were", "west", "what", "when", "whom", "wide",
            "wife", "wild", "will", "wind", "wine", "wing", "wire", "wise",
            "wish", "with", "wood", "word", "wore", "work", "yard", "year",
            "your", "zone"
        ]
        
        # Common English words for 5 letters - curated list
        words_5 = [
            # Basic concepts
            "happy", "world", "smart", "brain", "think", "dream",
            "peace", "quiet", "storm", "light", "night", "fight", "right",
            
            # Very common English words only
            "about", "above", "actor", "adult", "after", "again", "agent", "agree", "ahead", "alarm",
            "album", "alert", "alike", "alive", "allow", "alone", "along",
            "alter", "among", "anger", "angle", "angry", "apart", "apple",
            "apply", "argue", "arise", "array", "aside", "audio", "avoid", "award", "aware", "badly",
            "basic", "basis", "beach", "began", "begin", "begun",
            "being", "below", "bench", "birth", "black", "blame",
            "blind", "block", "blood", "board", "boost", "booth", "bound",
            "brain", "brand", "bread", "break", "breed", "brief", "bring",
            "broad", "broke", "brown", "build", "built", "buyer", "cable",
            "carry", "catch", "cause", "chain", "chair", "chart", "chase",
            "cheap", "check", "chest", "chief", "child", "china", "chose",
            "civil", "claim", "class", "clean", "clear", "click", "clock",
            "close", "coach", "coast", "could", "count", "court", "cover",
            "craft", "crash", "cream", "crime", "cross", "crowd", "crown",
            "curve", "cycle", "daily", "dance", "dealt", "death",
            "debut", "delay", "depth", "doing", "doubt", "dozen", "draft",
            "drama", "drawn", "dream", "dress", "drill", "drink", "drive", "drove",
            "dying", "eager", "early", "earth", "eight", "elite", "empty",
            "enemy", "enjoy", "enter", "entry", "equal", "error", "event",
            "every", "exact", "exist", "extra", "faith", "false", "fault",
            "field", "fifth", "fifty", "fight", "final", "first", "fixed",
            "flash", "fleet", "floor", "fluid", "focus", "force", "forth",
            "forty", "forum", "found", "frame", "frank", "fresh",
            "front", "fruit", "fully", "funny", "given", "glass",
            "globe", "going", "grace", "grade", "grand", "grant", "grass",
            "great", "green", "gross", "group", "grown", "guard", "guess",
            "guest", "guide", "happy", "heart", "heavy", "hence",
            "horse", "hotel", "house", "human", "ideal", "image", "index",
            "inner", "input", "issue", "joint", "judge", "known", "label",
            "large", "laser", "later", "laugh", "layer", "learn", "lease",
            "least", "leave", "legal", "level", "light", "limit",
            "links", "lives", "local", "logic", "loose", "lower", "lucky",
            "lunch", "lying", "magic", "major", "maker", "march", "maria",
            "match", "maybe", "mayor", "meant", "media", "metal", "might",
            "minor", "minus", "mixed", "model", "money", "month", "moral",
            "motor", "mount", "mouse", "mouth", "movie", "music", "needs",
            "never", "newly", "night", "noise", "north", "noted", "novel",
            "nurse", "occur", "ocean", "offer", "often", "order", "other",
            "ought", "paint", "panel", "paper", "party", "peace",
            "phase", "phone", "photo", "piece", "pilot", "pitch", "place",
            "plain", "plane", "plant", "plate", "point", "pound", "power",
            "press", "price", "pride", "prime", "print", "prior", "prize",
            "proof", "proud", "prove", "queen", "quick", "quiet", "quite",
            "radio", "raise", "range", "rapid", "ratio", "reach", "ready",
            "refer", "right", "rival", "river", "rough", "round",
            "route", "royal", "rural", "scale", "scene", "scope", "score",
            "sense", "serve", "seven", "shall", "shape", "share", "sharp",
            "sheet", "shelf", "shell", "shift", "shirt", "shock", "shoot",
            "short", "shown", "sight", "since", "sixth", "sixty", "sized",
            "skill", "sleep", "slide", "small", "smart", "smile", "smoke",
            "solid", "solve", "sorry", "sound", "south", "space", "spare",
            "speak", "speed", "spend", "spent", "split", "spoke", "sport",
            "staff", "stage", "stake", "stand", "start", "state", "steam",
            "steel", "stick", "still", "stock", "stone", "stood", "store",
            "storm", "story", "strip", "stuck", "study", "stuff", "style", "sugar",
            "suite", "super", "sweet", "table", "taken", "taste", "taxes",
            "teach", "teeth", "thank", "theft", "their",
            "theme", "there", "these", "thick", "thing", "think", "third", "those",
            "three", "threw", "throw", "tight", "times", "tired", "title",
            "today", "topic", "total", "touch", "tough", "tower", "track",
            "trade", "train", "treat", "trend", "trial", "tried", "tries",
            "truck", "truly", "trust", "truth", "twice", "under",
            "union", "unity", "until", "upper", "upset", "urban", "usage",
            "usual", "valid", "value", "video", "virus", "visit", "vital",
            "voice", "waste", "watch", "water", "wheel", "where", "which",
            "while", "white", "whole", "whose", "woman", "women", "world", "worry",
            "worse", "worst", "worth", "would", "wound", "write", "wrong",
            "wrote", "yield", "young", "youth"
        ]
        
        # Add all words to the custom words set in uppercase and lowercase
        for word in words_4:
            if self._is_good_english_word(word.upper()):
                self.custom_words.add(word.lower())
                self.custom_words.add(word.upper())
            
        for word in words_5:
            if self._is_good_english_word(word.upper()):
                self.custom_words.add(word.lower())
                self.custom_words.add(word.upper())
    
    def is_valid_word(self, word: str) -> bool:
        """Check if a word is valid for the game using multiple sources.
        
        Args:
            word: The word to validate
            
        Returns:
            True if the word is valid, False otherwise
        """
        if not word or not isinstance(word, str):
            return False
            
        # Accept both uppercase and lowercase
        word = word.strip()
        
        # Check word length
        if len(word) < self.min_word_length or len(word) > self.max_word_length:
            return False
        
        # Check if word contains only letters
        if not re.match(r'^[a-zA-Z]+$', word):
            return False
        
        word_upper = word.upper()
        word_lower = word.lower()
        
        # Check if word is excluded
        if word_upper in self._excluded_words:
            return False
        
        # Check if already cached
        if word_upper in self._wordnet_cache:
            return self._wordnet_cache[word_upper]
        
        # First check custom dictionary (for compatibility and quality)
        if word_upper in self.custom_words or word_lower in self.custom_words:
            self._wordnet_cache[word_upper] = True
            return True
        
        # Check filtered NLTK words corpus
        if self._nltk_words_cache and word_upper in self._nltk_words_cache:
            self._wordnet_cache[word_upper] = True
            return True
        
        # Check WordNet as final option, but still apply filters
        if wordnet.synsets(word_lower):
            if self._is_good_english_word(word_upper):
                self._wordnet_cache[word_upper] = True
                return True
        
        # Cache negative result
        self._wordnet_cache[word_upper] = False
        return False
    
    def is_one_letter_change(self, word1: str, word2: str) -> bool:
        """Check if two words differ by exactly one letter.
        
        Args:
            word1: The first word
            word2: The second word
            
        Returns:
            True if the words differ by exactly one letter, False otherwise
        """
        if len(word1) != len(word2):
            return False
            
        # Compare uppercase versions
        word1 = word1.upper()
        word2 = word2.upper()
        
        differences = 0
        for c1, c2 in zip(word1, word2):
            if c1 != c2:
                differences += 1
                if differences > 1:
                    return False
                    
        return differences == 1
    
    def get_possible_words(self, word: str) -> List[str]:
        """Get all possible valid words that differ by one letter from the given word.
        
        Args:
            word: The source word
            
        Returns:
            List of valid words that differ by one letter
        """
        word = word.upper()
        possible_words = []
        
        # For each position in the word
        for i in range(len(word)):
            # Try replacing with each letter of the alphabet
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if letter == word[i]:
                    continue
                    
                new_word = word[:i] + letter + word[i+1:]
                if self.is_valid_word(new_word):
                    possible_words.append(new_word)
        
        return possible_words
    
    def get_common_words(self, length: int, limit: int = 500) -> Set[str]:
        """Get common words of a specific length for game generation.
        
        Args:
            length: Word length
            limit: Maximum number of words
            
        Returns:
            Set of common words
        """
        # Use cache if available
        if length in self._filtered_words_cache:
            cached_words = self._filtered_words_cache[length]
            return set(list(cached_words)[:limit])
        
        # Get words from custom dictionary first (highest quality)
        custom_words_of_length = [
            word for word in self.custom_words 
            if len(word) == length and word.isupper()
        ]
        
        # Add filtered NLTK words
        if self._nltk_words_cache:
            nltk_words_of_length = [
                word for word in self._nltk_words_cache 
                if len(word) == length
            ]
            
            # Combine but prioritize custom words
            all_words = custom_words_of_length + [
                word for word in nltk_words_of_length 
                if word not in custom_words_of_length
            ]
        else:
            all_words = custom_words_of_length
        
        # Take the best ones (already filtered)
        result = set(all_words[:limit])
        
        # Cache the result
        self._filtered_words_cache[length] = result
        
        logger.info(f"Generated {len(result)} common words of length {length}")
        return result
    
    def can_reach_target(self, start_word: str, target_word: str, max_depth: int = 10) -> bool:
        """Check if target word can be reached from start word using BFS.
        
        Args:
            start_word: Starting word
            target_word: Target word
            max_depth: Maximum search depth
            
        Returns:
            True if target can be reached
        """
        if len(start_word) != len(target_word):
            return False
        
        start_word = start_word.upper()
        target_word = target_word.upper()
        
        if start_word == target_word:
            return True
        
        visited = {start_word}
        queue = [start_word]
        depth = 0
        
        while queue and depth < max_depth:
            next_queue = []
            
            for current_word in queue:
                possible_words = self.get_possible_words(current_word)
                
                for neighbor in possible_words:
                    if neighbor == target_word:
                        return True
                    
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_queue.append(neighbor)
            
            queue = next_queue
            depth += 1
        
        return False
    
    def add_word(self, word: str):
        """Add a new word to the custom dictionary.
        
        Args:
            word: The word to add
        """
        if self._is_good_english_word(word.upper()):
            self.custom_words.add(word.lower())
            self.custom_words.add(word.upper())
    
    def get_word_difficulty(self, word: str) -> float:
        """Calculate the difficulty score of a word based on frequency and length.
        
        Args:
            word: The word to evaluate
            
        Returns:
            A difficulty score (higher means more difficult)
        """
        word = word.lower()
        
        # Base difficulty on word length
        length_factor = min(1.0, (len(word) - self.min_word_length) / 
                          (self.max_word_length - self.min_word_length))
        
        # Simple difficulty scoring based on vowel to consonant ratio
        vowels = sum(1 for c in word if c in 'aeiou')
        consonants = len(word) - vowels
        if consonants == 0:
            ratio = 1.0
        else:
            ratio = vowels / consonants
        
        # Words with balanced vowel-consonant ratio are easier
        balance_factor = abs(0.5 - ratio) * 2  # 0 = perfectly balanced, 1 = very unbalanced
        
        # Combine factors (length and balance)
        difficulty = 0.6 * length_factor + 0.4 * balance_factor
        
        return difficulty