// Sound effects
const sounds = {
  click: new Audio(
    "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiL0fPTgjMGJYHH8N2QQAoUXrTp66hVFApGn+Dy"
  ),
  success: new Audio("data:audio/wav;base64,UklGRl9oAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YTtoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="),
  error: new Audio("data:audio/wav;base64,UklGRl9oAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YTtoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="),
  celebration: new Audio("data:audio/wav;base64,UklGRl9oAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YTtoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
};

// Sound functions
function playSound(soundName) {
  if (sounds[soundName]) {
    const sound = sounds[soundName].cloneNode();
    sound.volume = 0.3;
    sound.play().catch((e) => console.log("Sound play failed:", e));
  }
}

// Confetti animation
function createConfetti() {
  const celebration = document.getElementById("celebration");
  celebration.innerHTML = "";

  const colors = ["#FFD700", "#FF69B4", "#00CED1", "#FF4500", "#32CD32"];

  for (let i = 0; i < 100; i++) {
    const confetti = document.createElement("div");
    confetti.className = "confetti";
    confetti.style.left = Math.random() * 100 + "vw";
    confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
    confetti.style.animationDelay = Math.random() * 3 + "s";
    confetti.style.animationDuration = Math.random() * 3 + 2 + "s";
    celebration.appendChild(confetti);
  }

  setTimeout(() => {
    celebration.innerHTML = "";
  }, 5000);
}

// Game variables
let currentGameId = null;
let gameWords = [];
let startWord = "";
let targetWord = "";
let gameCompleted = false;
let selectedMode = "";
let selectedDifficulty = "";
const USE_MOCK_API = false;

// ✅ คำศัพท์ที่จำเป็นสำหรับการตรวจสอบคำ - เก็บเฉพาะคำที่สำคัญ
const CRITICAL_WORDS = {
  4: new Set([
    // คำที่จำเป็นสำหรับเส้นทาง COLD->WARM
    "COLD", "CORD", "WORD", "WORM", "WARM", "WOLD", "WILD", "WELD", "WIND",
    "CARD", "WARD", "WARE", "WORE", "WORT", "COLT", "BOLT", "BOLE", "BORE", "BARE",
    
    // คำที่จำเป็นสำหรับเส้นทาง BANK->LOAN
    "BANK", "BAND", "LAND", "LOAD", "LOAN", "BALD", "BOLD",
    
    // คำที่จำเป็นสำหรับเส้นทาง BIRD->FISH
    "BIRD", "BIND", "FIND", "FISH", "FIST", "BEST", "NEST",
    
    // คำที่จำเป็นสำหรับเส้นทาง FAST->SLOW
    "FAST", "LAST", "LOST", "SLOT", "SLOW", "CAST", "COST", "SHOT",
    
    // คำที่จำเป็นสำหรับเส้นทาง ROCK->SAND
    "ROCK", "SOCK", "SACK", "SANK", "SAND", "RACK", "RANK",
    
    // คำที่จำเป็นสำหรับเส้นทาง LEAD->GOLD
    "LEAD", "LOAD", "GOAD", "GOLD", "ROAD", "READ",
    
    // คำทั่วไปที่มีประโยชน์สำหรับการเชื่อมต่อ
    "ABLE", "BAKE", "CAKE", "DALE", "EASE", "FACE", "GAME", "HATE", "JADE", "KALE",
    "LAKE", "MAKE", "NAME", "PACE", "RACE", "SAFE", "TAKE", "VALE", "WAKE", "ZONE",
    "BANE", "CANE", "DANE", "FANE", "JANE", "LANE", "MANE", "PANE", "SANE", "VANE",
    "BASE", "CASE", "LASE", "VASE", "WISE", "ROSE", "POSE", "NOSE", "LOSE", "DOSE",
    "BONE", "CONE", "DONE", "GONE", "HONE", "LONE", "NONE", "TONE", "PONE", "ZONE",
    "BORE", "CORE", "FORE", "GORE", "LORE", "MORE", "PORE", "SORE", "TORE", "WORE",
    "BOLE", "COLE", "DOLE", "HOLE", "MOLE", "POLE", "ROLE", "SOLE", "TOLE", "VOLE"
  ]),
  5: new Set([
    // คำที่จำเป็นสำหรับเส้นทาง HOUSE->RANCH
    "HOUSE", "MOUSE", "MOOSE", "LOOSE", "LANCE", "RANCH", "HORSE",
    
    // คำที่จำเป็นสำหรับเส้นทาง HAPPY->SMILE
    "HAPPY", "HARPY", "SHARP", "SHARE", "SHIRE", "SPIRE", "SMILE", "SHINE",
    
    // คำที่จำเป็นสำหรับเส้นทาง BRAIN->THINK
    "BRAIN", "BRUIN", "BRINK", "THINK", "THING", "BRING",
    
    // คำที่จำเป็นสำหรับเส้นทาง OCEAN->WATER
    "OCEAN", "CLEAN", "CLEAR", "WATER", "LATER", "CATER",
    
    // คำทั่วไปที่มีประโยชน์สำหรับการเชื่อมต่อ
    "PLACE", "GRACE", "SPACE", "TRACE", "BRACE", "PEACE", "PIECE", "SLICE", "PRICE",
    "PLANE", "CRANE", "GRAIN", "TRAIN", "STAIN", "CHAIN", "PLAIN", "SPAIN", "PAINT",
    "PLANT", "GRANT", "GIANT", "SLANT", "POINT", "JOINT", "SAINT", "FAINT", "QUART",
    "PLATE", "STATE", "SLATE", "GRATE", "CRATE", "SKATE", "STAKE", "SNAKE", "SHAKE",
    "PRIDE", "BRIDE", "GUIDE", "SLIDE", "GLIDE", "ASIDE", "WIDE", "RIDE", "TIDE",
    "PRIME", "CRIME", "GRIME", "SLIME", "CHIME", "TIME", "DIME", "LIME", "MIME"
  ])
};

// ✅ ฟังก์ชันตรวจสอบคำที่เรียบง่าย
function isValidWord(word) {
  const wordLength = word.length;
  if (wordLength !== 4 && wordLength !== 5) return false;
  
  const upperWord = word.toUpperCase();
  return CRITICAL_WORDS[wordLength].has(upperWord);
}

// Helper function to switch screens
function switchScreen(screenId) {
  document.querySelectorAll(".screen").forEach((screen) => {
    screen.classList.remove("active");
  });
  const targetScreen = document.getElementById(screenId);
  if (targetScreen) {
    targetScreen.classList.add("active");
  }
}

// Navigation functions
function showModeScreen() {
  playSound("click");
  switchScreen("mode-screen");
}

function selectMode(mode) {
  playSound("click");
  selectedMode = mode;
  switchScreen("difficulty-screen");
}

function selectDifficulty(difficulty) {
  playSound("click");
  selectedDifficulty = difficulty;
  const wordLength = difficulty === "EASY" ? 4 : 5;
  createGame(wordLength, difficulty, selectedMode);
}

// Helper function to check localStorage availability
function isLocalStorageAvailable() {
  try {
    const test = "__storage_test__";
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}

// Theme toggle
function toggleTheme() {
  document.body.classList.toggle("dark-mode");
  if (isLocalStorageAvailable()) {
    localStorage.setItem(
      "theme",
      document.body.classList.contains("dark-mode") ? "dark" : "light"
    );
  }
  playSound("click");
}

// Create game function
async function createGame(wordLength, difficulty, gameMode) {
  gameCompleted = false;

  if (USE_MOCK_API) {
    mockCreateGame(wordLength, difficulty, gameMode);
    return;
  }

  try {
    const response = await fetch("/games/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        word_length: wordLength,
        difficulty: difficulty,
        game_mode: gameMode,
        player_id: null,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to create game");
    }

    const gameData = await response.json();
    processGameData(gameData);
  } catch (error) {
    console.error("Error creating game:", error);
    alert("Failed to create game. Please try again.");
    switchScreen("difficulty-screen");
  }
}

// ✅ Mock create game function - เก็บเฉพาะคู่คำที่การันตี
function mockCreateGame(wordLength, difficulty, gameMode) {
  const GUARANTEED_PAIRS = {
    4: {
      EASY: [["COLD", "WARM"], ["BANK", "LOAN"], ["FAST", "SLOW"], ["BIRD", "NEST"]],
      MEDIUM: [["ROCK", "SAND"], ["LEAD", "GOLD"], ["FISH", "MEAT"]],
      HARD: [["WINE", "CORK"], ["MIND", "SOUL"]]
    },
    5: {
      EASY: [["HOUSE", "RANCH"], ["HAPPY", "SMILE"], ["OCEAN", "WATER"]],
      MEDIUM: [["MOUSE", "TIGER"], ["BRAIN", "THINK"], ["POWER", "LIGHT"]],
      HARD: [["SHARP", "BLUNT"], ["QUICK", "SNAIL"]]
    }
  };

  const pairs = GUARANTEED_PAIRS[wordLength.toString()][difficulty];
  const [mockStartWord, mockTargetWord] = pairs[Math.floor(Math.random() * pairs.length)];

  const mockGameData = {
    game_id: "mock-" + Date.now(),
    start_word: mockStartWord,
    target_word: mockTargetWord,
    current_word: mockStartWord,
    difficulty: difficulty,
    game_mode: gameMode,
    moves_count: 0,
    moves: [],
    status: "IN_PROGRESS",
  };

  processGameData(mockGameData);
}

// Process game data
function processGameData(gameData) {
  currentGameId = gameData.game_id;
  startWord = gameData.start_word.toUpperCase();
  targetWord = gameData.target_word.toUpperCase();

  document.getElementById("display-start-word").textContent = startWord;
  document.getElementById("display-target-word").textContent = targetWord;
  document.getElementById("display-current-word").textContent = startWord;
  document.getElementById("display-moves-count").textContent = "0";

  gameWords = [startWord];

  document.getElementById("game-error").textContent = "";
  document.getElementById("game-message").textContent = "Game started! Try to reach the target word.";
  document.getElementById("hint-text").textContent = "";
  document.getElementById("next-word").value = "";
  document.getElementById("timer-display").style.display = "none";

  updateWordGrid();
  switchScreen("game-container");

  if (selectedMode === "TIMED") {
    startTimer();
  }
}

// Restart game function
function restartGame() {
  document.getElementById("congrats-modal").style.display = "none";
  resetGameState();
  switchScreen("welcome-screen");
}

// Make move function
async function makeMove() {
  if (gameCompleted || !currentGameId) {
    return;
  }

  const nextWordEl = document.getElementById("next-word");
  const nextWord = nextWordEl.value.trim().toUpperCase();
  
  if (!nextWord) {
    document.getElementById("game-error").textContent = "Please enter a word";
    playSound("error");
    return;
  }

  document.getElementById("game-error").textContent = "";

  if (USE_MOCK_API) {
    mockMakeMove(nextWord);
    return;
  }

  try {
    const response = await fetch(`/games/${currentGameId}/move`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ word: nextWord }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Invalid move");
    }

    const moveData = await response.json();
    processMoveData(moveData);
  } catch (error) {
    console.error("Error making move:", error);
    document.getElementById("game-error").textContent = error.message;
    playSound("error");
  }
}

// Mock make move function
function mockMakeMove(nextWord) {
  const currentWord = gameWords[gameWords.length - 1];
  
  if (nextWord.length !== currentWord.length) {
    document.getElementById("game-error").textContent = "Word must be same length as current word";
    playSound("error");
    return;
  }

  // ตรวจสอบว่าเปลี่ยนแปลงเพียง 1 ตัวอักษร
  let diffCount = 0;
  for (let i = 0; i < currentWord.length; i++) {
    if (currentWord[i] !== nextWord[i]) diffCount++;
  }

  if (diffCount !== 1) {
    document.getElementById("game-error").textContent = "You can only change one letter at a time";
    playSound("error");
    return;
  }

  // ตรวจสอบว่าคำมีอยู่จริง
  if (!isValidWord(nextWord)) {
    document.getElementById("game-error").textContent = "Not a valid word";
    playSound("error");
    return;
  }

  // ตรวจสอบว่าใช้คำซ้ำหรือไม่
  if (gameWords.includes(nextWord)) {
    document.getElementById("game-error").textContent = "Word already used";
    playSound("error");
    return;
  }

  const isTarget = nextWord === targetWord;
  const mockMoveData = {
    word: nextWord,
    is_target: isTarget,
    message: isTarget ? "Congratulations! You reached the target word!" : "Good move!",
    moves_count: gameWords.length,
    path: [...gameWords, nextWord],
    valid: true,
  };

  processMoveData(mockMoveData);
}

// Process move data
function processMoveData(moveData) {
  document.getElementById("display-current-word").textContent = moveData.word.toUpperCase();
  document.getElementById("next-word").value = "";
  document.getElementById("game-message").textContent = moveData.message;
  document.getElementById("display-moves-count").textContent = moveData.moves_count;

  gameWords.push(moveData.word.toUpperCase());
  playSound("success");
  updateWordGrid();

  if (moveData.is_target) {
    gameCompleted = true;
    stopTimer();
    showCongratulationsModal();
  }
}

// Show congratulations modal
function showCongratulationsModal() {
  document.getElementById("modal-start-word").textContent = startWord;
  document.getElementById("modal-target-word").textContent = targetWord;
  document.getElementById("modal-moves-count").textContent = gameWords.length - 1;
  document.getElementById("modal-path").textContent = gameWords.join(" → ");

  document.getElementById("congrats-modal").style.display = "block";
  playSound("celebration");
  createConfetti();
}

// ✅ Get hint function - ใช้ BFS ง่ายๆ
async function getHint() {
  if (gameCompleted || !currentGameId) return;

  document.getElementById("game-error").textContent = "";

  if (USE_MOCK_API) {
    mockGetHint();
    return;
  }

  try {
    const response = await fetch(`/games/${currentGameId}/hint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ hint_level: 3 }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to get hint");
    }

    const hintData = await response.json();
    document.getElementById("hint-text").textContent = hintData.hint_text;
  } catch (error) {
    console.error("Error getting hint:", error);
    document.getElementById("game-error").textContent = error.message;
    playSound("error");
  }
}

// ✅ Mock get hint function - BFS อย่างง่าย
function mockGetHint() {
  const currentWord = gameWords[gameWords.length - 1];
  const queue = [[currentWord]];
  const visited = new Set([currentWord, ...gameWords]); // รวมคำที่ใช้แล้ว
  let foundPath = null;

  while (queue.length > 0 && !foundPath) {
    const path = queue.shift();
    const lastWord = path[path.length - 1];

    if (lastWord === targetWord) {
      foundPath = path;
      break;
    }

    // ลองเปลี่ยนแต่ละตำแหน่ง
    for (let i = 0; i < lastWord.length; i++) {
      for (let charCode = 65; charCode <= 90; charCode++) {
        const newChar = String.fromCharCode(charCode);
        if (newChar !== lastWord[i]) {
          const newWord = lastWord.substring(0, i) + newChar + lastWord.substring(i + 1);

          if (isValidWord(newWord) && !visited.has(newWord)) {
            visited.add(newWord);
            queue.push([...path, newWord]);
          }
        }
      }
    }
  }

  if (foundPath && foundPath.length > 1) {
    const nextWord = foundPath[1];
    let position = -1;
    let newLetter = "";
    
    for (let i = 0; i < currentWord.length; i++) {
      if (currentWord[i] !== nextWord[i]) {
        position = i;
        newLetter = nextWord[i];
        break;
      }
    }

    if (position !== -1) {
      document.getElementById("hint-text").textContent = 
        `Try changing position ${position + 1} from '${currentWord[position]}' to '${newLetter}' → '${nextWord}'`;
    } else {
      document.getElementById("hint-text").textContent = 
        "Keep trying! Look for valid words by changing one letter.";
    }
  } else {
    document.getElementById("hint-text").textContent = 
      "Keep trying! Look for valid words by changing one letter.";
  }
}

// Update word grid function
function updateWordGrid() {
  const gridContainer = document.getElementById("word-grid");
  if (!gridContainer) return;

  gridContainer.innerHTML = "";
  if (gameWords.length === 0) return;

  gameWords.forEach((word, wordIndex) => {
    const wordRow = document.createElement("div");
    wordRow.className = "word-row";

    for (let i = 0; i < word.length; i++) {
      const letterCell = document.createElement("div");
      letterCell.className = "letter-cell";
      letterCell.textContent = word[i];

      if (word[i] === targetWord[i]) {
        letterCell.classList.add("matched-target");
      }

      if (wordIndex === gameWords.length - 1) {
        letterCell.classList.add("current");
      }

      if (word === targetWord) {
        letterCell.classList.add("target");
      }

      if (wordIndex > 0 && word[i] !== gameWords[wordIndex - 1][i]) {
        letterCell.classList.add("changed");
      }

      wordRow.appendChild(letterCell);
    }

    gridContainer.appendChild(wordRow);
  });
}

// ✅ Timer functions
let gameTimer = null;
let timeLimit = 300; // 5 minutes
let timeRemaining = 0;

function startTimer() {
  if (selectedMode !== "TIMED") return;

  timeRemaining = timeLimit;
  document.getElementById("timer-display").style.display = "block";

  gameTimer = setInterval(() => {
    timeRemaining--;
    updateTimerDisplay();

    if (timeRemaining <= 0) {
      stopTimer();
      handleTimeUp();
    }
  }, 1000);
}

function updateTimerDisplay() {
  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;
  const timeString = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;

  const timeDisplay = document.getElementById("display-time-left");
  timeDisplay.textContent = timeString;

  if (timeRemaining <= 30) {
    timeDisplay.style.color = "#ff0000";
    timeDisplay.style.fontWeight = "bold";
  } else if (timeRemaining <= 60) {
    timeDisplay.style.color = "#ff8800";
  }
}

function handleTimeUp() {
  gameCompleted = true;
  document.getElementById("game-message").textContent = "Time's up! Game over.";
  document.getElementById("game-message").style.color = "#ff4444";
  document.getElementById("submit-move-btn").disabled = true;
  document.getElementById("next-word").disabled = true;

  playSound("error");
  setTimeout(() => showTimeUpModal(), 1000);
}

function showTimeUpModal() {
  const modal = document.getElementById("congrats-modal");
  const title = modal.querySelector("h2");
  const message = modal.querySelector(".congrats-message");

  title.textContent = "⏰ Time's Up!";
  title.style.color = "#ff4444";
  message.textContent = "You ran out of time! Better luck next time.";

  document.getElementById("modal-start-word").textContent = startWord;
  document.getElementById("modal-target-word").textContent = targetWord;
  document.getElementById("modal-moves-count").textContent = gameWords.length - 1;
  document.getElementById("modal-path").textContent = gameWords.join(" → ");

  modal.style.display = "block";
}

function stopTimer() {
  if (gameTimer) {
    clearInterval(gameTimer);
    gameTimer = null;
  }
}

// ✅ Reset game state
function resetGameState() {
  stopTimer();
  currentGameId = null;
  gameWords = [];
  startWord = "";
  targetWord = "";
  gameCompleted = false;
  selectedMode = "";
  selectedDifficulty = "";
  timeRemaining = 0;

  // Clear UI
  ["display-start-word", "display-target-word", "display-current-word", 
   "game-error", "game-message", "hint-text", "next-word"].forEach(id => {
    const element = document.getElementById(id);
    if (element) element.textContent = "";
  });

  document.getElementById("display-moves-count").textContent = "0";
  document.getElementById("timer-display").style.display = "none";
  document.getElementById("submit-move-btn").disabled = false;
  document.getElementById("next-word").disabled = false;

  const gridContainer = document.getElementById("word-grid");
  if (gridContainer) gridContainer.innerHTML = "";
}

// ✅ Confirmation modal
let confirmationCallback = null;

function showConfirmationModal(message, onConfirm) {
  document.getElementById("confirmation-modal").style.display = "block";
  confirmationCallback = onConfirm;
  playSound("click");
}

function hideConfirmationModal() {
  document.getElementById("confirmation-modal").style.display = "none";
}

function goBackToPreviousScreen(currentScreen, previousScreen) {
  playSound("click");

  if (currentScreen === "game-container" && !gameCompleted) {
    showConfirmationModal("Are you sure you want to exit the game?", function () {
      resetGameState();
      switchScreen("welcome-screen");
    });
  } else {
    switchScreen(previousScreen);
  }
}

// ✅ Event listeners
document.addEventListener("DOMContentLoaded", function () {
  // Load theme
  if (isLocalStorageAvailable()) {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      document.body.classList.add("dark-mode");
    }
  }

  // Theme toggle
  document.getElementById("theme-toggle-btn")?.addEventListener("click", toggleTheme);

  // Navigation
  document.getElementById("start-game-btn")?.addEventListener("click", showModeScreen);

  // Mode buttons
  document.getElementById("mode-classic")?.addEventListener("click", () => selectMode("CLASSIC"));
  document.getElementById("mode-timed")?.addEventListener("click", () => selectMode("TIMED"));

  // Difficulty buttons
  document.getElementById("diff-easy")?.addEventListener("click", () => selectDifficulty("EASY"));
  document.getElementById("diff-medium")?.addEventListener("click", () => selectDifficulty("MEDIUM"));
  document.getElementById("diff-hard")?.addEventListener("click", () => selectDifficulty("HARD"));

  // Game buttons
  document.getElementById("submit-move-btn")?.addEventListener("click", makeMove);
  document.getElementById("get-hint-btn")?.addEventListener("click", getHint);
  document.getElementById("restart-btn")?.addEventListener("click", restartGame);

  // Enter key for word input
  document.getElementById("next-word")?.addEventListener("keyup", function (event) {
    if (event.key === "Enter") makeMove();
  });

  // Back buttons
  document.getElementById("back-from-mode-btn")?.addEventListener("click", () =>
    goBackToPreviousScreen("mode-screen", "welcome-screen"));
  document.getElementById("back-from-difficulty-btn")?.addEventListener("click", () =>
    goBackToPreviousScreen("difficulty-screen", "mode-screen"));
  document.getElementById("back-from-game-btn")?.addEventListener("click", () => {
    const targetScreen = gameCompleted ? "welcome-screen" : "difficulty-screen";
    goBackToPreviousScreen("game-container", targetScreen);
  });

  // Confirmation modal buttons
  document.getElementById("confirm-yes-btn")?.addEventListener("click", function () {
    if (confirmationCallback) {
      const callback = confirmationCallback;
      confirmationCallback = null;
      hideConfirmationModal();
      callback();
    } else {
      hideConfirmationModal();
    }
  });

  document.getElementById("confirm-no-btn")?.addEventListener("click", function () {
    confirmationCallback = null;
    hideConfirmationModal();
    playSound("click");
  });
});