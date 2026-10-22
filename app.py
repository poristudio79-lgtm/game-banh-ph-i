import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Bóng Đá 3D Siêu Sao", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; }
    iframe { border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    </style>
""", unsafe_allow_html=True)

# Giao diện HTML + Three.js 3D Game không gian nhỏ, cầu thủ chân thực
GAME_3D_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
    body { background: #0b0f19; color: #fff; font-family: 'Segoe UI', Tahoma, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }
    #gameContainer { position: relative; width: 900px; height: 550px; background: #111; border-radius: 12px; overflow: hidden; border: 3px solid #333; }
    canvas { display: block; width: 100%; height: 100%; }
    
    /* Overlay Screen */
    .screen { position: absolute; inset: 0; background: rgba(10, 15, 30, 0.92); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; transition: all 0.3s ease; }
    .hidden { display: none !important; opacity: 0; pointer-events: none; }
    
    h1 { font-size: 38px; margin-bottom: 25px; color: #ffeb3b; text-shadow: 0 0 15px rgba(255,235,59,0.5); letter-spacing: 2px; }
    h2 { font-size: 26px; margin-bottom: 15px; color: #00e676; }
    
    /* Menu PLAY Button (Hình chữ nhật) */
    .btn-play { width: 240px; height: 60px; background: linear-gradient(135deg, #00e676, #00b0ff); border: none; border-radius: 10px; color: #fff; font-size: 24px; font-weight: bold; cursor: pointer; box-shadow: 0 6px 20px rgba(0,230,118,0.4); transition: transform 0.2s, box-shadow 0.2s; display: flex; align-items: center; justify-content: center; letter-spacing: 1px; }
    .btn-play:hover { transform: translateY(-3px) scale(1.03); box-shadow: 0 10px 25px rgba(0,230,118,0.6); }

    /* Player Selection Grid */
    .player-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; width: 90%; max-width: 760px; margin-top: 10px; }
    .player-card { background: rgba(255,255,255,0.06); border: 2px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 12px 6px; text-align: center; cursor: pointer; transition: all 0.2s; }
    .player-card:hover { border-color: #00e676; background: rgba(0,230,118,0.15); transform: translateY(-4px); }
    .player-avatar { width: 45px; height: 45px; border-radius: 50%; margin: 0 auto 6px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; border: 2px solid #fff; }
    .player-name { font-size: 13px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .player-team { font-size: 10px; color: #aaa; margin-top: 2px; }

    /* In-game HUD */
    #hud { position: absolute; top: 15px; left: 20px; right: 20px; display: flex; justify-content: space-between; font-size: 16px; font-weight: bold; z-index: 5; pointer-events: none; }
    .badge { background: rgba(0,0,0,0.6); padding: 8px 15px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); }
</style>
<!-- Thư viện Three.js 3D -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

<div id="gameContainer">
    <!-- HUD Điểm số -->
    <div id="hud">
        <div class="badge" id="playerInfo">⚽ Cầu thủ: -</div>
        <div class="badge" id="scoreInfo">Bàn thắng: 0 | Lượt: 0</div>
    </div>

    <!-- MÀN HÌNH 1: MENU CHÍNH -->
    <div id="menuScreen" class="screen">
        <h1>⚽ 3D PENALTY SHOOTOUT</h1>
        <button class="btn-play" onclick="openPlayerSelect()">PLAY</button>
    </div>

    <!-- MÀN HÌNH 2: CHỌN 10 CẦU THỦ NỔI TIẾNG -->
    <div id="selectScreen" class="screen hidden">
        <h2>CHỌN SIÊU SAO RA SÂN</h2>
        <div class="player-grid" id="playerGrid"></div>
    </div>
</div>

<script>
const PLAYERS = [
    { name: "K. Mbappé", team: "Real Madrid", jersey: 9, shirtColor: 0xffffff, skinColor: 0x8d5524, hairColor: 0x111111 },
    { name: "L. Messi", team: "Inter Miami", jersey: 10, shirtColor: 0xf7a8b8, skinColor: 0xffdbac, hairColor: 0x3b2219 },
    { name: "C. Ronaldo", team: "Al Nassr", jersey: 7, shirtColor: 0xffe600, skinColor: 0xe0ac69, hairColor: 0x111111 },
    { name: "E. Haaland", team: "Man City", jersey: 9, shirtColor: 0x6cabdd, skinColor: 0xffdbac, hairColor: 0xf3e5ab },
    { name: "L. Yamal", team: "Barcelona", jersey: 19, shirtColor: 0xa50044, skinColor: 0x8d5524, hairColor: 0x111111 },
    { name: "Vinícius Jr.", team: "Real Madrid", jersey: 7, shirtColor: 0xffffff, skinColor: 0x5c3826, hairColor: 0x111111 },
    { name: "J. Bellingham", team: "Real Madrid", jersey: 5, shirtColor: 0xffffff, skinColor: 0x8d5524, hairColor: 0x1c1c1c },
    { name: "H. Kane", team: "Bayern Munich", jersey: 9, shirtColor: 0xdc052d, skinColor: 0xffdbac, hairColor: 0xd4af37 },
    { name: "O. Dembélé", team: "PSG", jersey: 10, shirtColor: 0x004170, skinColor: 0x5c3826, hairColor: 0x111111 },
    { name: "M. Salah", team: "Liverpool", jersey: 11, shirtColor: 0xc8102e, skinColor: 0x8d5524, hairColor: 0x221100 }
];

let selectedPlayer = null;
let score = 0, attempts = 0;
let gameState = 'MENU'; // MENU, SELECT, AIM, KICKING, RESULT

// Khởi tạo giao diện danh sách cầu thủ
function initGrid() {
    const grid = document.getElementById('playerGrid');
    grid.innerHTML = '';
    PLAYERS.forEach(p => {
        const card = document.createElement('div');
        card.className = 'player-card';
        card.onclick = () => selectPlayer(p);
        card.innerHTML = `
            <div class="player-avatar" style="background:#${p.shirtColor.toString(16)}; color:${p.shirtColor===0xffffff?'#000':'#fff'}">${p.jersey}</div>
            <div class="player-name">${p.name}</div>
            <div class="player-team">${p.team}</div>
        `;
        grid.appendChild(card);
    });
}

function openPlayerSelect() {
    document.getElementById('menuScreen').classList.add('hidden');
    document.getElementById('selectScreen').classList.remove('hidden');
    initGrid();
}

function selectPlayer(player) {
    selectedPlayer = player;
    document.getElementById('selectScreen').classList.add('hidden');
    document.getElementById('playerInfo').innerText = `⚽ ${player.name} (#${player.jersey})`;
    buildStrikerMesh();
    gameState = 'AIM';
}

// --- THREE.JS 3D SCENE SETUP ---
const container = document.getElementById('gameContainer');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1329);
scene.fog = new THREE.Fog(0x0b1329, 15, 30);

const camera = new THREE.PerspectiveCamera(50, 900 / 550, 0.1, 1000);
camera.position.set(0, 3.5, 9);
camera.lookAt(0, 1.5, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(900, 550);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

// Ánh sáng
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(5, 12, 5);
dirLight.castShadow = true;
scene.add(dirLight);

// Sân cỏ thu nhỏ ấm cúng
const pitchGeo = new THREE.PlaneGeometry(16, 20);
const pitchMat = new THREE.MeshStandardMaterial({ color: 0x1e7e34, roughness: 0.8 });
const pitch = new THREE.Mesh(pitchGeo, pitchMat);
pitch.rotation.x = -Math.PI / 2;
pitch.receiveShadow = true;
scene.add(pitch);

// Khung thành nhỏ
const goalGroup = new THREE.Group();
goalGroup.position.set(0, 0, -6);
const postMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
const barGeo = new THREE.CylinderGeometry(0.08, 0.08, 5.2);
const leftPost = new THREE.Mesh(barGeo, postMat); leftPost.position.set(-2.6, 1.3, 0); leftPost.castShadow = true;
const rightPost = new THREE.Mesh(barGeo, postMat); rightPost.position.set(2.6, 1.3, 0); rightPost.castShadow = true;
const crossGeo = new THREE.CylinderGeometry(0.08, 0.08, 5.3); crossGeo.rotateZ(Math.PI / 2);
const crossbar = new THREE.Mesh(crossGeo, postMat); crossbar.position.set(0, 2.6, 0); crossbar.castShadow = true;
goalGroup.add(leftPost, rightPost, crossbar);
scene.add(goalGroup);

// Quả bóng 3D
const ballGeo = new THREE.SphereGeometry(0.22, 24, 24);
const ballMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
const ball = new THREE.Mesh(ballGeo, ballMat);
ball.position.set(0, 0.22, 3);
ball.castShadow = true;
scene.add(ball);

// Thủ môn 3D
const keeperGroup = new THREE.Group();
const keeperBodyMat = new THREE.MeshStandardMaterial({ color: 0xffeb3b });
const keeperBody = new THREE.Mesh(new THREE.BoxGeometry(0.7, 1.1, 0.3), keeperBodyMat);
keeperBody.position.y = 1.2;
const keeperHead = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 16), new THREE.MeshStandardMaterial({ color: 0xffdbac }));
keeperHead.position.y = 1.9;
keeperGroup.add(keeperBody, keeperHead);
keeperGroup.position.set(0, 0, -5.7);
scene.add(keeperGroup);

// Cầu thủ 3D chi tiết
let strikerGroup = new THREE.Group();
scene.add(strikerGroup);

function buildStrikerMesh() {
    while(strikerGroup.children.length > 0){ strikerGroup.remove(strikerGroup.children[0]); }
    if (!selectedPlayer) return;

    const mat = new THREE.MeshStandardMaterial({ color: selectedPlayer.shirtColor });
    const skinMat = new THREE.MeshStandardMaterial({ color: selectedPlayer.skinColor });
    const hairMat = new THREE.MeshStandardMaterial({ color: selectedPlayer.hairColor });

    // Thân
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.0, 0.3), mat);
    body.position.y = 1.1;
    body.castShadow = true;

    // Đầu & Tóc đặc trưng
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), skinMat);
    head.position.y = 1.85;
    const hair = new THREE.Mesh(new THREE.SphereGeometry(0.23, 16, 16), hairMat);
    hair.position.set(0, 1.92, -0.03);
    hair.scale.set(1, 0.7, 1.1);

    // Chân
    const legGeo = new THREE.BoxGeometry(0.2, 0.9, 0.2);
    const leftLeg = new THREE.Mesh(legGeo, skinMat); leftLeg.position.set(-0.2, 0.45, 0);
    const rightLeg = new THREE.Mesh(legGeo, skinMat); rightLeg.position.set(0.2, 0.45, 0);

    strikerGroup.add(body, head, hair, leftLeg, rightLeg);
    strikerGroup.position.set(0, 0, 3.8);
}

// Điều khiển sút bằng chuột
let targetAim = { x: 0, y: 1.5 };
window.addEventListener('mousemove', (e) => {
    if (gameState !== 'AIM') return;
    const rect = container.getBoundingClientRect();
    let x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    let y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    targetAim.x = x * 2.3;
    targetAim.y = Math.max(0.3, Math.min(2.3, y * 1.5 + 1.2));
});

window.addEventListener('click', () => {
    if (gameState !== 'AIM') return;
    gameState = 'KICKING';
});

let kickProgress = 0;
let keeperTargetX = 0;

// Game Loop 3D
function animate() {
    requestAnimationFrame(animate);

    if (gameState === 'KICKING') {
        kickProgress += 0.05;
        // Cầu thủ chạy nhẹ tới sút
        strikerGroup.position.z -= 0.08;

        if (kickProgress >= 1) {
            gameState = 'FLYING';
            keeperTargetX = (Math.random() - 0.5) * 3.5;
        }
    }

    if (gameState === 'FLYING') {
        // Bóng bay về phía khung thành và hướng ngắm
        ball.position.x += (targetAim.x - ball.position.x) * 0.08;
        ball.position.y += (targetAim.y - ball.position.y) * 0.08;
        ball.position.z += (-6 - ball.position.z) * 0.08;
        ball.rotation.x += 0.2;

        // Thủ môn bay người cản phá
        keeperGroup.position.x += (keeperTargetX - keeperGroup.position.x) * 0.1;

        // Kiểm tra kết quả khi bóng tới gần vạch vôi
        if (ball.position.z <= -5.6) {
            gameState = 'RESULT';
            attempts++;
            let saved = Math.abs(ball.position.x - keeperGroup.position.x) < 0.9 && ball.position.y < 2.3;

            if (!saved && Math.abs(ball.position.x) <= 2.6 && ball.position.y <= 2.6) {
                score++;
                alert("⚽ VÀOOOOOO! Siêu phẩm đẳng cấp!");
            } else {
                alert("❌ CẢN PHÁ! Thủ môn đã bay người xuất sắc!");
            }

            document.getElementById('scoreInfo').innerText = `Bàn thắng: ${score} | Lượt: ${attempts}`;
            
            setTimeout(() => {
                ball.position.set(0, 0.22, 3);
                strikerGroup.position.set(0, 0, 3.8);
                keeperGroup.position.set(0, 0, -5.7);
                kickProgress = 0;
                gameState = 'AIM';
            }, 1000);
        }
    }

    renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
"""

components.html(GAME_3D_HTML, height=580)
