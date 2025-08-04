<!-- hands_on_thorns.html with Online Mode -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hands on Thorns</title>
  <link rel="stylesheet" href="style.css">
  <script src="https://accounts.google.com/gsi/client" async defer></script>
  <script src="https://cdn.socket.io/4.6.1/socket.io.min.js" integrity="sha384-+SkNU6Af2Xf5/oyhvmLgbjqU4xR3TozYYeX0cuVCnv0V6Gp1yP1zU8dHtZtNd+oJ" crossorigin="anonymous"></script>
</head>
<body>
  <div id="login-container">
    <div id="g_id_onload"
        data-client_id="YOUR_GOOGLE_CLIENT_ID"
        data-login_uri="http://localhost:5000/google-login"
        data-auto_prompt="false">
    </div>
    <div class="g_id_signin" data-type="standard"></div>
  </div>

  <div id="app" style="display:none;">
    <div>
      <label><input type="checkbox" id="stealModeToggle"> Enable Stealing Mode</label>
    </div>
    <h1>Hands on Thorns - <span id="mode">Offline</span> Mode</h1>
    <button onclick="startOnlineGame()">Switch to Online Mode</button>
    <div id="info">
      <span id="score">Score: 0</span>
      <span id="timer">Time: 30</span>
    </div>
    <div id="grid"></div>
    <div id="result" style="display:none;"></div>
    <button id="restart" style="display:none;">Play Again</button>
  </div>

  <script>
    const grid = document.getElementById("grid");
    const scoreDisplay = document.getElementById("score");
    const timerDisplay = document.getElementById("timer");
    const resultDisplay = document.getElementById("result");
    const restartBtn = document.getElementById("restart");
    const modeDisplay = document.getElementById("mode");

    let score = 0;
    let missed = 0;
    let timeLeft = 120;
    let interval;
    let flashTimeout;
    let socket;
    const size = 5;
    let online = false;

    function createGrid() {
      grid.innerHTML = "";
      grid.style.display = "grid";
      grid.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
      grid.style.gap = "6px";
      for (let i = 0; i < size * size; i++) {
        const cell = document.createElement("div");
        cell.classList.add("cell");
        cell.dataset.index = i;
        grid.appendChild(cell);
      }
    }

    function flashDot(index = null) {
      const cells = document.querySelectorAll(".cell");
      cells.forEach(cell => cell.classList.remove("active"));
      const rand = index !== null ? index : Math.floor(Math.random() * cells.length);
      const dot = cells[rand];
      dot.classList.add("active");
      dot.onclick = () => {
        if (dot.classList.contains("active")) {
          score++;
          dot.classList.remove("active");
          scoreDisplay.textContent = `Score: ${score} | Missed: ${missed}`;
          if (online) socket.emit("steal", { index: rand });
          scoreDisplay.textContent = `Score: ${score} | Missed: ${missed}`;
          dot.classList.remove("active");
          if (online) socket.emit("hit", { score });
        }
      };
      flashTimeout = setTimeout(() => {
        if (dot.classList.contains("active")) {
          score--;
          missed++;
          scoreDisplay.textContent = `Score: ${score} | Missed: ${missed}`;
        }
        dot.classList.remove("active");
        dot.onclick = null;
      }, 1000);
    }

    function updateTimer() {
      timeLeft--;
      timerDisplay.textContent = `Time: ${timeLeft}`;
      if (timeLeft <= 0) {
        clearInterval(interval);
        clearTimeout(flashTimeout);
        document.querySelectorAll(".cell").forEach(cell => cell.onclick = null);
        resultDisplay.style.display = "block";
        resultDisplay.textContent = `Game Over!
Final Score: ${score}
Dots Missed: ${missed}`;
        restartBtn.style.display = "inline-block";
        if (online) socket.emit("game_over", { score });
      }
    }

    function startGame() {
      score = 0;
      timeLeft = 30;
      missed = 0;
      scoreDisplay.textContent = "Score: 0 | Missed: 0";
      timerDisplay.textContent = "Time: 120";
      resultDisplay.style.display = "none";
      restartBtn.style.display = "none";
      createGrid();
      interval = setInterval(() => {
        if (online) return; // server controls dot
        flashDot();
        updateTimer();
      }, 1000);
    }

    function startOnlineGame() {
      const stealEnabled = document.getElementById("stealModeToggle").checked;
      if (!socket) {
        socket = io("http://localhost:5000");
        socket.on("connect", () => console.log("Connected to server"));
        socket.on("dot", data => flashDot(data.index));
        socket.on("start", () => {
          modeDisplay.textContent = "Online";
          online = true;
          startGame();
        });
        socket.emit("join_game", { stealMode: stealEnabled });
      } else {
        socket.emit("join_game");
      }
    }

    restartBtn.onclick = () => {
      if (online) {
        socket.emit("join_game");
      } else {
        startGame();
      }
    };

    window.onload = function () {
      window.handleCredentialResponse = (response) => {
        document.getElementById("login-container").style.display = "none";
        document.getElementById("app").style.display = "block";
        startGame();
      };
    };
  </script>

  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #1a1a1a;
      color: white;
      text-align: center;
      padding: 20px;
    }
    #grid {
      margin: 20px auto;
      max-width: 400px;
    }
    .cell {
      background: #333;
      width: 100%;
      padding-top: 100%;
      position: relative;
      border: 1px solid #555;
      cursor: pointer;
    }
    .cell.active {
      background: red;
    }
    .cell::after {
      content: '';
      display: block;
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
    }
    #info {
      font-size: 20px;
      margin: 10px;
      display: flex;
      justify-content: space-around;
    }
    button {
      padding: 10px 20px;
      font-size: 18px;
      cursor: pointer;
      margin-top: 10px;
    }
  </style>
</body>
</html>
