const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const coinsEl = document.getElementById("coins");
const livesEl = document.getElementById("lives");
const statusEl = document.getElementById("status");
const restartBtn = document.getElementById("restart");

const GRAVITY = 0.65;
const TILE = 48;

const keys = { left: false, right: false, jump: false };

const levelWidth = 3000;
const groundY = 460;

const state = {
  cameraX: 0,
  score: 0,
  lives: 3,
  ended: false,
};

const player = {
  x: 120,
  y: 0,
  w: 36,
  h: 44,
  vx: 0,
  vy: 0,
  speed: 5,
  jump: 14,
  grounded: false,
  invuln: 0,
};

const platforms = [
  { x: 0, y: groundY, w: levelWidth, h: 80 },
  { x: 300, y: 360, w: TILE * 2, h: TILE / 2 },
  { x: 550, y: 310, w: TILE * 2, h: TILE / 2 },
  { x: 900, y: 370, w: TILE * 3, h: TILE / 2 },
  { x: 1300, y: 320, w: TILE * 2, h: TILE / 2 },
  { x: 1700, y: 290, w: TILE * 3, h: TILE / 2 },
  { x: 2200, y: 340, w: TILE * 2, h: TILE / 2 },
];

const coins = [
  [350, 300], [400, 300], [610, 250], [960, 320], [1030, 320],
  [1360, 260], [1760, 230], [1830, 230], [1900, 230], [2250, 280]
].map(([x, y]) => ({ x, y, r: 10, got: false }));

const enemies = [
  { x: 700, y: groundY - 32, w: 34, h: 32, minX: 660, maxX: 860, vx: 1.3, dead: false },
  { x: 1480, y: groundY - 32, w: 34, h: 32, minX: 1440, maxX: 1640, vx: 1.6, dead: false },
  { x: 2350, y: groundY - 32, w: 34, h: 32, minX: 2300, maxX: 2550, vx: 1.8, dead: false },
];

const flag = { x: 2850, y: 180, w: 16, h: 280 };

function rectsCollide(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function resetPositions() {
  player.x = 120;
  player.y = 200;
  player.vx = 0;
  player.vy = 0;
  state.cameraX = 0;
}

function fullReset() {
  state.score = 0;
  state.lives = 3;
  state.ended = false;
  statusEl.textContent = "플레이 중";
  coins.forEach((c) => (c.got = false));
  enemies.forEach((e) => (e.dead = false));
  resetPositions();
  updateHud();
}

function updateHud() {
  coinsEl.textContent = String(state.score);
  livesEl.textContent = String(state.lives);
}

function hitPlayer() {
  if (player.invuln > 0 || state.ended) return;
  state.lives -= 1;
  updateHud();
  if (state.lives <= 0) {
    state.ended = true;
    statusEl.textContent = "게임 오버";
    return;
  }
  player.invuln = 90;
  resetPositions();
}

function updatePlayer() {
  player.vx = 0;
  if (keys.left) player.vx = -player.speed;
  if (keys.right) player.vx = player.speed;

  if (keys.jump && player.grounded) {
    player.vy = -player.jump;
    player.grounded = false;
  }

  player.vy += GRAVITY;

  player.x += player.vx;
  player.y += player.vy;

  player.grounded = false;
  for (const p of platforms) {
    if (!rectsCollide(player, p)) continue;

    if (player.vy > 0 && player.y + player.h - player.vy <= p.y) {
      player.y = p.y - player.h;
      player.vy = 0;
      player.grounded = true;
    } else if (player.vy < 0 && player.y - player.vy >= p.y + p.h) {
      player.y = p.y + p.h;
      player.vy = 0;
    } else if (player.vx > 0) {
      player.x = p.x - player.w;
    } else if (player.vx < 0) {
      player.x = p.x + p.w;
    }
  }

  if (player.y > canvas.height + 100) {
    hitPlayer();
  }

  player.x = Math.max(0, Math.min(levelWidth - player.w, player.x));
  state.cameraX = Math.max(0, Math.min(levelWidth - canvas.width, player.x - 260));

  if (player.invuln > 0) player.invuln -= 1;
}

function updateCoins() {
  for (const c of coins) {
    if (c.got) continue;
    const box = { x: c.x - c.r, y: c.y - c.r, w: c.r * 2, h: c.r * 2 };
    if (rectsCollide(player, box)) {
      c.got = true;
      state.score += 1;
      updateHud();
    }
  }
}

function updateEnemies() {
  for (const e of enemies) {
    if (e.dead) continue;
    e.x += e.vx;
    if (e.x < e.minX || e.x > e.maxX) e.vx *= -1;

    if (!rectsCollide(player, e)) continue;

    const stomp = player.vy > 0 && player.y + player.h - player.vy <= e.y + 8;
    if (stomp) {
      e.dead = true;
      player.vy = -9;
    } else {
      hitPlayer();
    }
  }
}

function updateGoal() {
  if (!state.ended && rectsCollide(player, flag)) {
    state.ended = true;
    statusEl.textContent = "클리어!";
  }
}

function drawBackground() {
  ctx.fillStyle = "#8fd3ff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < 8; i++) {
    const x = (i * 380 - state.cameraX * 0.25) % (canvas.width + 380);
    const y = 70 + (i % 3) * 40;
    ctx.fillStyle = "rgba(255,255,255,0.9)";
    ctx.beginPath();
    ctx.ellipse(x, y, 45, 25, 0, 0, Math.PI * 2);
    ctx.ellipse(x + 35, y + 8, 40, 20, 0, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawWorld() {
  ctx.save();
  ctx.translate(-state.cameraX, 0);

  ctx.fillStyle = "#24aa38";
  for (const p of platforms) ctx.fillRect(p.x, p.y, p.w, p.h);

  ctx.fillStyle = "#d4a75f";
  for (const p of platforms) if (p.y !== groundY) ctx.fillRect(p.x, p.y, p.w, 10);

  for (const c of coins) {
    if (c.got) continue;
    ctx.fillStyle = "#ffd84a";
    ctx.beginPath();
    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#d69700";
    ctx.stroke();
  }

  for (const e of enemies) {
    if (e.dead) continue;
    ctx.fillStyle = "#7e4a1f";
    ctx.fillRect(e.x, e.y, e.w, e.h);
    ctx.fillStyle = "#fff";
    ctx.fillRect(e.x + 7, e.y + 9, 7, 7);
    ctx.fillRect(e.x + 20, e.y + 9, 7, 7);
  }

  ctx.fillStyle = "#f9f9f9";
  ctx.fillRect(flag.x, flag.y, flag.w, flag.h);
  ctx.fillStyle = "#f04c2f";
  ctx.beginPath();
  ctx.moveTo(flag.x + 16, flag.y + 20);
  ctx.lineTo(flag.x + 110, flag.y + 45);
  ctx.lineTo(flag.x + 16, flag.y + 72);
  ctx.closePath();
  ctx.fill();

  const blink = player.invuln > 0 && Math.floor(player.invuln / 6) % 2 === 0;
  if (!blink) {
    ctx.fillStyle = "#e22d2d";
    ctx.fillRect(player.x, player.y, player.w, player.h);
    ctx.fillStyle = "#ffcf96";
    ctx.fillRect(player.x + 6, player.y + 8, player.w - 12, 18);
  }

  ctx.restore();
}

function tick() {
  if (!state.ended) {
    updatePlayer();
    updateCoins();
    updateEnemies();
    updateGoal();
  }
  drawBackground();
  drawWorld();
  requestAnimationFrame(tick);
}

window.addEventListener("keydown", (e) => {
  if (e.code === "ArrowLeft") keys.left = true;
  if (e.code === "ArrowRight") keys.right = true;
  if (e.code === "Space" || e.code === "ArrowUp") keys.jump = true;
});

window.addEventListener("keyup", (e) => {
  if (e.code === "ArrowLeft") keys.left = false;
  if (e.code === "ArrowRight") keys.right = false;
  if (e.code === "Space" || e.code === "ArrowUp") keys.jump = false;
});

restartBtn.addEventListener("click", fullReset);

fullReset();
requestAnimationFrame(tick);
