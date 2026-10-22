import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Đá Bánh 2D", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
    }
    iframe {
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Giao diện HTML5 Canvas + JavaScript Game nhúng trực tiếp vào Streamlit
GAME_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
    body { background: #000; color: #fff; font-family: 'Segoe UI', Tahoma, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }
    #gameContainer { position: relative; width: 800px; height: 500px; background: #111; border-radius: 12px; overflow: hidden; border: 3px solid #333; }
    canvas { display: block; width: 100%; height: 100%; }
    
    /* Overlay Screen */
    .screen { position: absolute; inset: 0; background: rgba(10, 15, 30, 0.95); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; transition: all 0.3s ease; }
    .hidden { display: none !important; opacity: 0; pointer-events: none; }
    
    h1 { font-size: 40px; margin-bottom: 20px; color: #ffeb3b; text-shadow: 0 0 15px rgba(255,235,59,0.5); }
    h2 { font-size: 28px; margin-bottom: 15px; color: #00e676; }
    
    /* Menu Play Button */
    .btn-play { width: 220px; height: 65px; background: linear-gradient(135deg, #00e676, #00b0ff); border: none; border-radius: 12px; color: #fff; font-size: 24px; font-weight: bold; cursor: pointer; box-shadow: 0 6px 20px rgba(0,230,118,0.4); transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .btn-play:hover { transform: translateY(-3px) scale(1.03); box-shadow: 0 10px 25px rgba(0,230,118,0.6); }
    .btn-play span { font-size: 11px; opacity: 0.9; font-weight: normal; margin-top: 2px; }

    /* Player Selection Grid */
    .player-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; width: 90%; max-width: 720px; margin-top: 10px; }
    .player-card { background: rgba(255,255,255,0.08); border: 2px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 10px 5px; text-align: center; cursor: pointer; transition: all 0.2s; }
    .player-card:hover { border-color: #00e676; background: rgba(0,230,118,0.15); transform: translateY(-4px); }
    .player-avatar { width: 50px; height: 50px; border-radius: 50%; margin: 0 auto 5px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; border: 2px solid #fff; }
    .player-name { font-size: 12px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .player-team { font-size: 10px; color: #aaa; }

    /* In-game HUD */
    #hud { position: absolute; top: 15px; left: 20px; right: 20px; display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; z-index: 5; pointer-events: none; }
    .badge { background: rgba(0,0,0,0.6); padding: 8px 15px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); }
</style>
</head>
<body>

<div id="gameContainer">
    <!-- Canvas Vẽ Sân Bóng & Cầu Thủ -->
    <canvas id="canvas" width="800" height="500"></canvas>

    <!-- HUD Điểm Số -->
    <div id="hud">
        <div class="badge" id="playerInfo">⚽ Cầu thủ: -</div>
        <div class="badge" id="scoreInfo">Bàn thắng: 0 / Lượt sút: 0</div>
    </div>

    <!-- MÀN HÌNH 1: MENU CHÍNH -->
    <div id="menuScreen" class="screen">
        <h1>⚽ PENALTY SHOOTOUT</h1>
        <button class="btn-play" onclick="openPlayerSelect()">
            PLAY
            <span>BẮT ĐẦU TRẬN ĐẤU</span>
        </button>
    </div>

    <!-- MÀN HÌNH 2: CHỌN CẦU THỦ (10 CẦU THỦ CHIẾN NHẤT) -->
    <div id="selectScreen" class="screen hidden">
        <h2>CHỌN CẦU THỦ SÚT BÓNG</h2>
        <div class="player-grid" id="playerGrid"></div>
    </div>
</div>

<script>
const PLAYERS = [
    { name: "K. Mbappé", team: "Real Madrid", jersey: 9, color: "#ffffff", skin: "#8d5524" },
    { name: "L. Messi", team: "Inter Miami", jersey: 10, color: "#f7a8b8", skin: "#ffdbac" },
    { name: "C. Ronaldo", team: "Al Nassr", jersey: 7, color: "#ffe600", skin: "#e0ac69" },
    { name: "E. Haaland", team: "Man City", jersey: 9, color: "#6cabdd", skin: "#ffdbac" },
    { name: "L. Yamal", team: "Barcelona", jersey: 19, color: "#a50044", skin: "#8d5524" },
    { name: "Vinícius Jr.", team: "Real Madrid", jersey: 7, color: "#ffffff", skin: "#5c3826" },
    { name: "J. Bellingham", team: "Real Madrid", jersey: 5, color: "#ffffff", skin: "#8d5524" },
    { name: "H. Kane", team: "Bayern Munich", jersey: 9, color: "#dc052d", skin: "#ffdbac" },
    { name: "O. Dembélé", team: "PSG", jersey: 10, color: "#004170", skin: "#5c3826" },
    { name: "M. Salah", team: "Liverpool", jersey: 11, color: "#c8102e", skin: "#8d5524" }
];

let selectedPlayer = null;
let score = 0, attempts = 0;
let gameState = 'MENU'; // MENU, SELECT, AIM, ANIMATING, RESULT

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Trạng thái vật lý
let ball = { x: 400, y: 400, z: 1, vx: 0, vy: 0, vz: 0, radius: 14, angle: 0 };
let striker = { x: 340, y: 410, legAngle: 0, state: 'IDLE', runProgress: 0 };
let keeper = { x: 400, y: 190, vx: 0, targetX: 400 };
let targetPoint = { x: 400, y: 180 };
let aimAngle = 0;

function initPlayerGrid() {
    const grid = document.getElementById('playerGrid');
    grid.innerHTML = '';
    PLAYERS.forEach((p, idx) => {
        const card = document.createElement('div');
        card.className = 'player-card';
        card.onclick = () => selectPlayer(p);
        card.innerHTML = `
            <div class="player-avatar" style="background:${p.color}; color:${p.color==='#ffffff'?'#000':'#fff'}">${p.jersey}</div>
            <div class="player-name">${p.name}</div>
            <div class="player-team">${p.team}</div>
        `;
        grid.appendChild(card);
    });
}

function openPlayerSelect() {
    document.getElementById('menuScreen').classList.add('hidden');
    document.getElementById('selectScreen').classList.remove('hidden');
    initPlayerGrid();
}

function selectPlayer(player) {
    selectedPlayer = player;
    document.getElementById('selectScreen').classList.add('hidden');
    document.getElementById('playerInfo').innerText = `⚽ ${player.name} (#${player.jersey})`;
    resetRound();
    gameState = 'AIM';
}

function resetRound() {
    ball = { x: 400, y: 400, z: 1, vx: 0, vy: 0, vz: 0, radius: 14, angle: 0 };
    striker = { x: 340, y: 410, legAngle: 0, state: 'IDLE', runProgress: 0 };
    keeper = { x: 400, y: 190, vx: 0, targetX: 400 };
    targetPoint = { x: 400, y: 170 };
    aimAngle = 0;
}

// Bắt sự kiện click để sút
canvas.addEventListener('mousemove', (e) => {
    if (gameState !== 'AIM') return;
    const rect = canvas.getBoundingClientRect();
    targetPoint.x = e.clientX - rect.left;
    targetPoint.y = Math.min(e.clientY - rect.top, 220); // Giới hạn khu vực khung thành
});

canvas.addEventListener('click', () => {
    if (gameState !== 'AIM') return;
    gameState = 'RUNNING';
    striker.state = 'RUN';
});

// Vẽ sân bóng
function drawPitch() {
    // Cỏ sân
    let grad = ctx.createLinearGradient(0, 0, 0, 500);
    grad.addColorStop(0, '#1b4d1b');
    grad.addColorStop(1, '#2e7d32');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 800, 500);

    // Kẻ vạch sân & Vòng cấm
    ctx.strokeStyle = "rgba(255,255,255,0.6)";
    ctx.lineWidth = 3;
    ctx.strokeRect(180, 120, 440, 140); // Khung vạch cấm
    
    // Khung thành
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 6;
    ctx.strokeRect(260, 110, 280, 80);
    
    // Lưới khung thành
    ctx.strokeStyle = "rgba(255,255,255,0.2)";
    ctx.lineWidth = 1;
    for(let x=260; x<=540; x+=15) { ctx.beginPath(); ctx.moveTo(x, 110); ctx.lineTo(x, 190); ctx.stroke(); }
    for(let y=110; y<=190; y+=10) { ctx.beginPath(); ctx.moveTo(260, y); ctx.lineTo(540, y); ctx.stroke(); }

    // Chấm penalty
    ctx.fillStyle = "#fff";
    ctx.beginPath(); ctx.arc(400, 400, 4, 0, Math.PI*2); ctx.fill();
}

// Vẽ Cầu thủ sút bóng
function drawStriker() {
    if (!selectedPlayer) return;
    ctx.save();
    ctx.translate(striker.x, striker.y);

    // Áo cầu thủ
    ctx.fillStyle = selectedPlayer.color;
    ctx.fillRect(-10, -35, 20, 25);

    // Đầu cầu thủ
    ctx.fillStyle = selectedPlayer.skin;
    ctx.beginPath(); ctx.arc(0, -42, 8, 0, Math.PI*2); ctx.fill();

    // Chân & Động tác sút bóng
    ctx.strokeStyle = selectedPlayer.skin;
    ctx.lineWidth = 5;
    
    // Chân trụ
    ctx.beginPath(); ctx.moveTo(-4, -10); ctx.lineTo(-6, 10); ctx.stroke();

    // Chân sút
    ctx.beginPath();
    ctx.moveTo(4, -10);
    let legX = 4 + Math.sin(striker.legAngle) * 15;
    let legY = 10 - Math.cos(striker.legAngle) * 5;
    ctx.lineTo(legX, legY);
    ctx.stroke();

    // Số áo
    ctx.fillStyle = selectedPlayer.color === '#ffffff' ? '#000' : '#fff';
    ctx.font = 'bold 10px sans-serif';
    ctx.fillText(selectedPlayer.jersey, -3, -20);

    ctx.restore();
}

// Vẽ Thủ môn
function drawKeeper() {
    ctx.save();
    ctx.translate(keeper.x, keeper.y);
    // Áo thủ môn màu vàng
    ctx.fillStyle = "#ffeb3b";
    ctx.fillRect(-12, -30, 24, 25);
    // Đầu
    ctx.fillStyle = "#ffdbac";
    ctx.beginPath(); ctx.arc(0, -36, 8, 0, Math.PI*2); ctx.fill();
    // Tay dang rộng
    ctx.strokeStyle = "#ffeb3b";
    ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(-12, -22); ctx.lineTo(-22, -10); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(12, -22); ctx.lineTo(22, -10); ctx.stroke();
    ctx.restore();
}

// Vẽ Trái bóng tròn hoạ tiết đen trắng
function drawBall() {
    ctx.save();
    ctx.translate(ball.x, ball.y);
    ctx.scale(ball.z, ball.z);
    
    // Bóng râm
    ctx.fillStyle = "rgba(0,0,0,0.3)";
    ctx.beginPath();
    ctx.ellipse(0, 12, ball.radius, ball.radius/2, 0, 0, Math.PI*2);
    ctx.fill();

    // Quả bóng chính
    ctx.rotate(ball.angle);
    ctx.fillStyle = "#ffffff";
    ctx.beginPath(); ctx.arc(0, 0, ball.radius, 0, Math.PI*2); ctx.fill();
    ctx.lineWidth = 1.5; ctx.strokeStyle = "#000"; ctx.stroke();

    // Hoạ tiết ngũ giác đen trên trái bóng
    ctx.fillStyle = "#000000";
    ctx.beginPath(); ctx.arc(0, 0, 5, 0, Math.PI*2); ctx.fill();
    for(let i=0; i<5; i++) {
        let a = (i * 72) * Math.PI / 180;
        ctx.beginPath();
        ctx.arc(Math.cos(a)*9, Math.sin(a)*9, 3, 0, Math.PI*2);
        ctx.fill();
    }
    ctx.restore();
}

// Đường ngắm sút
function drawAim() {
    if (gameState !== 'AIM') return;
    ctx.strokeStyle = "rgba(255, 255, 255, 0.5)";
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(ball.x, ball.y);
    ctx.lineTo(targetPoint.x, targetPoint.y);
    ctx.stroke();
    ctx.setLineDash([]);

    // Tâm ngắm
    ctx.strokeStyle = "#ffeb3b";
    ctx.beginPath(); ctx.arc(targetPoint.x, targetPoint.y, 8, 0, Math.PI*2); ctx.stroke();
}

// Loop Game Update
function update() {
    if (gameState === 'RUNNING') {
        // Cầu thủ chạy đà tới bóng
        striker.x += 3;
        striker.runProgress += 0.15;
        striker.legAngle = Math.sin(striker.runProgress) * 0.8;

        if (striker.x >= ball.x - 15) {
            // Sút bóng!
            gameState = 'KICKED';
            striker.legAngle = -1.2; // Chân vung ra sút
            
            // Tính toán quỹ đạo bóng
            let dx = targetPoint.x - ball.x;
            let dy = targetPoint.y - ball.y;
            ball.vx = dx / 25;
            ball.vy = dy / 25;
            
            // Thủ môn phán đoán bay người
            let keeperTargets = [targetPoint.x, 400 + (Math.random()*160 - 80)];
            keeper.targetX = keeperTargets[Math.floor(Math.random()*keeperTargets.length)];
        }
    }

    if (gameState === 'KICKED') {
        ball.x += ball.vx;
        ball.y += ball.vy;
        ball.z = Math.max(0.5, ball.z - 0.015); // Bóng xa dần
        ball.angle += 0.2; // Bóng xoay

        // Thủ môn di chuyển cản phá
        keeper.x += (keeper.targetX - keeper.x) * 0.12;

        // Kiểm tra bóng đến khung thành
        if (ball.y <= targetPoint.y) {
            gameState = 'RESULT';
            attempts++;
            
            // Kiểm tra xem Thủ môn cản được không
            let dist = Math.abs(ball.x - keeper.x);
            let isGoal = (ball.x >= 260 && ball.x <= 540 && ball.y >= 110 && ball.y <= 190) && dist > 35;

            if (isGoal) {
                score++;
                alert("⚽ VÀOOOOOO! Bàn thắng tuyệt đẹp!");
            } else {
                alert("❌ CẢN PHÁ! Cú sút không thắng được thủ môn!");
            }

            document.getElementById('scoreInfo').innerText = `Bàn thắng: ${score} / Lượt sút: ${attempts}`;
            setTimeout(() => {
                resetRound();
                gameState = 'AIM';
            }, 1000);
        }
    }
}

function render() {
    ctx.clearRect(0, 0, 800, 500);
    drawPitch();
    drawAim();
    drawKeeper();
    drawStriker();
    drawBall();
}

function gameLoop() {
    update();
    render();
    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
</body>
</html>
"""

# Nhúng Game vào Streamlit với chiều cao 550px
components.html(GAME_HTML, height=550)
