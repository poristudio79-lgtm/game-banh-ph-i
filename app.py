import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Bóng Đá 3D Siêu Sao", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; }
    iframe { border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    </style>
""", unsafe_allow_html=True)

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
    .screen { position: absolute; inset: 0; background: rgba(10, 15, 30, 0.95); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 100; transition: all 0.3s ease; }
    .hidden { display: none !important; opacity: 0; pointer-events: none; }
    
    h1 { font-size: 38px; margin-bottom: 25px; color: #ffeb3b; text-shadow: 0 0 15px rgba(255,235,59,0.5); letter-spacing: 2px; }
    h2 { font-size: 26px; margin-bottom: 15px; color: #00e676; }
    
    /* Menu PLAY Button */
    .btn-play { width: 240px; height: 60px; background: linear-gradient(135deg, #00e676, #00b0ff); border: none; border-radius: 10px; color: #fff; font-size: 24px; font-weight: bold; cursor: pointer; box-shadow: 0 6px 20px rgba(0,230,118,0.4); transition: transform 0.2s, box-shadow 0.2s; display: flex; align-items: center; justify-content: center; letter-spacing: 1px; z-index: 101; }
    .btn-play:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 10px 25px rgba(0,230,118,0.6); }

    /* Player Selection Grid */
    .player-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; width: 90%; max-width: 760px; margin-top: 10px; }
    .player-card { background: rgba(255,255,255,0.08); border: 2px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 12px 6px; text-align: center; cursor: pointer; transition: all 0.2s; z-index: 101; }
    .player-card:hover { border-color: #00e676; background: rgba(0,230,118,0.25); transform: translateY(-4px); }
    .player-avatar { width: 45px; height: 45px; border-radius: 50%; margin: 0 auto 6px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; border: 2px solid #fff; }
    .player-name { font-size: 13px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .player-team { font-size: 10px; color: #aaa; margin-top: 2px; }

    /* HUD */
    #hud { position: absolute; top: 15px; left: 20px; right: 20px; display: flex; justify-content: space-between; font-size: 16px; font-weight: bold; z-index: 5; pointer-events: none; }
    .badge { background: rgba(0,0,0,0.6); padding: 8px 15px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

<div id="gameContainer">
    <div id="hud">
        <div class="badge" id="playerInfo">⚽ Cầu thủ: -</div>
        <div class="badge" id="scoreInfo">Bàn thắng: 0 | Lượt: 0</div>
    </div>

    <!-- MENU CHÍNH -->
    <div id="menuScreen" class="screen">
        <h1>⚽ 3D PENALTY SHOOTOUT</h1>
        <button id="playBtn" class="btn-play">PLAY</button>
    </div>

    <!-- CHỌN CẦU THỦ -->
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
let gameState = 'MENU';

// SỰ KIỆN MENU
document.getElementById('playBtn').addEventListener('click', function(e) {
    e.stopPropagation();
    document.getElementById('menuScreen').classList.add('hidden');
    document.getElementById('selectScreen').classList.remove('hidden');
    initGrid();
});

function initGrid() {
    const grid = document.getElementById('playerGrid');
    grid.innerHTML = '';
    PLAYERS.forEach(p => {
        const card = document.createElement('div');
        card.className = 'player-card';
        card.onclick = (e) => {
            e.stopPropagation();
            selectPlayer(p);
        };
        card.innerHTML = `
            <div class="player-avatar" style="background:#${p.shirtColor.toString(16).padStart(6,'0')}; color:${p.shirtColor===0xffffff?'#000':'#fff'}">${p.jersey}</div>
            <div class="player-name">${p.name}</div>
            <div class="player-team">${p.team}</div>
        `;
        grid.appendChild(card);
    });
}

function selectPlayer(player) {
    selectedPlayer = player;
    document.getElementById('selectScreen').classList.add('hidden');
    document.getElementById('playerInfo').innerText = `⚽ ${player.name} (#${player.jersey})`;
    buildStrikerMesh();
    setTimeout(() => { gameState = 'AIM'; }, 200);
}

// THREE.JS SETUP
const container = document.getElementById('gameContainer');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1329);
scene.fog = new THREE.Fog(0x0b1329, 15, 35);

const camera = new THREE.PerspectiveCamera(50, 900 / 550, 0.1, 1000);
camera.position.set(0, 3.2, 8.8);
camera.lookAt(0, 1.4, -2);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(900, 550);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.7); scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.9); dirLight.position.set(5, 12, 5); dirLight.castShadow = true; scene.add(dirLight);

// SÂN CỎ
const pitchGeo = new THREE.PlaneGeometry(18, 22);
const pitchMat = new THREE.MeshStandardMaterial({ color: 0x1e7e34, roughness: 0.8 });
const pitch = new THREE.Mesh(pitchGeo, pitchMat); pitch.rotation.x = -Math.PI / 2; pitch.receiveShadow = true; scene.add(pitch);

// KHÁN GIẢ NHÚN NHẢY XUNG QUANH KHÁN ĐÀI
const crowdGroup = new THREE.Group();
const fans = [];
const crowdColors = [0xe74c3c, 0x3498db, 0xf1c40f, 0x2ecc71, 0x9b59b6, 0xffffff];

for(let i=0; i<120; i++) {
    const fanGeo = new THREE.BoxGeometry(0.3, 0.6, 0.3);
    const fanMat = new THREE.MeshBasicMaterial({ color: crowdColors[Math.floor(Math.random()*crowdColors.length)] });
    const fan = new THREE.Mesh(fanGeo, fanMat);
    
    let side = Math.random() > 0.5 ? 1 : -1;
    let dist = 6.5 + Math.random() * 2;
    let depth = -7.5 + Math.random() * 12;
    
    fan.position.set(side * dist, 0.8 + Math.random()*0.3, depth);
    fan.userData = { initialY: fan.position.y, speed: 0.05 + Math.random()*0.08, offset: Math.random()*Math.PI*2 };
    crowdGroup.add(fan);
    fans.push(fan);
}
scene.add(crowdGroup);

// KHUNG THÀNH VÀ LƯỚI
const goalGroup = new THREE.Group();
goalGroup.position.set(0, 0, -6);
const postMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });

const postGeo = new THREE.CylinderGeometry(0.08, 0.08, 2.6, 16);
const leftPost = new THREE.Mesh(postGeo, postMat); leftPost.position.set(-2.6, 1.3, 0); leftPost.castShadow = true;
const rightPost = new THREE.Mesh(postGeo, postMat); rightPost.position.set(2.6, 1.3, 0); rightPost.castShadow = true;

const crossGeo = new THREE.CylinderGeometry(0.08, 0.08, 5.36, 16); crossGeo.rotateZ(Math.PI / 2);
const crossbar = new THREE.Mesh(crossGeo, postMat); crossbar.position.set(0, 2.6, 0); crossbar.castShadow = true;
goalGroup.add(leftPost, rightPost, crossbar);

// Lưới
function createNetMaterial() {
    const canvas = document.createElement('canvas'); canvas.width = 64; canvas.height = 64;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#000000'; ctx.fillRect(0, 0, 64, 64);
    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(64,64); ctx.moveTo(64,0); ctx.lineTo(0,64); ctx.stroke();
    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping; texture.wrapT = THREE.RepeatWrapping;
    return new THREE.MeshBasicMaterial({ map: texture, transparent: true, opacity: 0.55, side: THREE.DoubleSide });
}
const netMat = createNetMaterial();
const backNetGeo = new THREE.PlaneGeometry(5.2, 2.6);
const backNetMat = netMat.clone(); backNetMat.map.repeat.set(15, 8);
const backNet = new THREE.Mesh(backNetGeo, backNetMat); backNet.position.set(0, 1.3, -1.6);
goalGroup.add(backNet);
scene.add(goalGroup);

// QUẢ BÓNG 3D
const ballGeo = new THREE.SphereGeometry(0.22, 24, 24);
const ballMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
const ball = new THREE.Mesh(ballGeo, ballMat);
ball.position.set(0, 0.22, 3.2);
ball.castShadow = true;
scene.add(ball);

// THỦ MÔN (ĐẦY ĐỦ THÂN, ĐẦU, 2 TAY VÀ 2 CHÂN)
const keeperGroup = new THREE.Group();
const keeperBodyMat = new THREE.MeshStandardMaterial({ color: 0xffeb3b });
const keeperSkinMat = new THREE.MeshStandardMaterial({ color: 0xffdbac });
const keeperPantMat = new THREE.MeshStandardMaterial({ color: 0x222222 });

const keeperBody = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.9, 0.3), keeperBodyMat); keeperBody.position.y = 1.15;
const keeperHead = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 16), keeperSkinMat); keeperHead.position.y = 1.8;

// Tay thủ môn
const armGeo = new THREE.BoxGeometry(0.18, 0.7, 0.18);
const keeperLeftArm = new THREE.Mesh(armGeo, keeperSkinMat); keeperLeftArm.position.set(-0.45, 1.1, 0); keeperLeftArm.rotation.z = 0.3;
const keeperRightArm = new THREE.Mesh(armGeo, keeperSkinMat); keeperRightArm.position.set(0.45, 1.1, 0); keeperRightArm.rotation.z = -0.3;

// Chân thủ môn
const legGeo = new THREE.BoxGeometry(0.22, 0.8, 0.22);
const keeperLeftLeg = new THREE.Mesh(legGeo, keeperPantMat); keeperLeftLeg.position.set(-0.2, 0.4, 0);
const keeperRightLeg = new THREE.Mesh(legGeo, keeperPantMat); keeperRightLeg.position.set(0.2, 0.4, 0);

keeperGroup.add(keeperBody, keeperHead, keeperLeftArm, keeperRightArm, keeperLeftLeg, keeperRightLeg);
keeperGroup.position.set(0, 0, -5.7);
scene.add(keeperGroup);

// CẦU THỦ SÚT BÓNG (ĐỨNG XÉO BÊN TRÁI 45 ĐỘ, ĐẦY ĐỦ TAY CHÂN)
let strikerGroup = new THREE.Group();
let rightLegMesh = null;
scene.add(strikerGroup);

function buildStrikerMesh() {
    while(strikerGroup.children.length > 0){ strikerGroup.remove(strikerGroup.children[0]); }
    if (!selectedPlayer) return;

    const mat = new THREE.MeshStandardMaterial({ color: selectedPlayer.shirtColor });
    const skinMat = new THREE.MeshStandardMaterial({ color: selectedPlayer.skinColor });
    const hairMat = new THREE.MeshStandardMaterial({ color: selectedPlayer.hairColor });

    // Thân & Đầu
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.0, 0.3), mat); body.position.y = 1.1; body.castShadow = true;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), skinMat); head.position.y = 1.85;
    const hair = new THREE.Mesh(new THREE.SphereGeometry(0.23, 16, 16), hairMat); hair.position.set(0, 1.92, -0.03); hair.scale.set(1, 0.7, 1.1);

    // Tay cầu thủ
    const armGeo = new THREE.BoxGeometry(0.18, 0.7, 0.18);
    const leftArm = new THREE.Mesh(armGeo, skinMat); leftArm.position.set(-0.42, 1.1, 0);
    const rightArm = new THREE.Mesh(armGeo, skinMat); rightArm.position.set(0.42, 1.1, 0);

    // Chân cầu thủ
    const legGeo = new THREE.BoxGeometry(0.2, 0.9, 0.2);
    const leftLeg = new THREE.Mesh(legGeo, skinMat); leftLeg.position.set(-0.2, 0.45, 0);
    rightLegMesh = new THREE.Mesh(legGeo, skinMat); rightLegMesh.position.set(0.2, 0.45, 0);

    strikerGroup.add(body, head, hair, leftArm, rightArm, leftLeg, rightLegMesh);
    
    // Đứng xéo bên trái 45 độ
    strikerGroup.position.set(-1.2, 0, 3.8);
    strikerGroup.rotation.y = 0.45; 
}

// BẮT ĐIỂM NGẮM TỰ DO KHẮC PHỤC LỖI SÚT 1 HƯỚNG
let targetAim = { x: 0, y: 1.3 };
let isTargeting = false;

container.addEventListener('mousemove', (e) => {
    if (gameState !== 'AIM') return;
    const rect = container.getBoundingClientRect();
    
    let mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    let mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    
    targetAim.x = mouseX * 3.2; 
    targetAim.y = Math.max(0.2, Math.min(2.8, mouseY * 1.8 + 1.4)); 
    isTargeting = true;
});

container.addEventListener('click', () => {
    if (gameState === 'AIM' && isTargeting) {
        gameState = 'KICKING';
    }
});

let kickProgress = 0;
let keeperTargetX = 0, keeperTargetY = 1.1;
let ballSpeedX = 0, ballSpeedY = 0, ballSpeedZ = 0;

let clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    let time = clock.getElapsedTime();

    // Khán giả nhún nhảy lên xuống
    fans.forEach(f => {
        f.position.y = f.userData.initialY + Math.sin(time * 8 * f.userData.speed + f.userData.offset) * 0.15;
    });

    if (gameState === 'KICKING') {
        kickProgress += 0.08;
        strikerGroup.position.x += 0.1;
        strikerGroup.position.z -= 0.05;

        if (kickProgress >= 1) {
            gameState = 'FLYING';
            
            ballSpeedX = (targetAim.x - ball.position.x) * 0.09;
            ballSpeedY = (targetAim.y - ball.position.y) * 0.09;
            ballSpeedZ = (-6.0 - ball.position.z) * 0.09;

            if(rightLegMesh) rightLegMesh.rotation.x = -1.2;

            keeperTargetX = (Math.random() - 0.5) * 3.8;
            keeperTargetY = Math.random() > 0.5 ? 1.6 : 0.6;
        }
    }

    if (gameState === 'FLYING') {
        ball.position.x += ballSpeedX;
        ball.position.y += ballSpeedY;
        ball.position.z += ballSpeedZ;
        ball.rotation.x += 0.25;

        keeperGroup.position.x += (keeperTargetX - keeperGroup.position.x) * 0.12;
        keeperGroup.position.y += (keeperTargetY - keeperGroup.position.y) * 0.12;
        keeperGroup.rotation.z = -(keeperTargetX * 0.15);

        if (ball.position.z <= -5.6) {
            gameState = 'RESULT';
            attempts++;
            
            let distToKeeper = Math.hypot(ball.position.x - keeperGroup.position.x, ball.position.y - keeperGroup.position.y);
            let saved = distToKeeper < 0.95;
            let isInsideGoal = Math.abs(ball.position.x) <= 2.6 && ball.position.y <= 2.6 && ball.position.y >= 0.1;

            if (!saved && isInsideGoal) {
                score++;
                alert("⚽ VÀOOOOOO! Cú sút tung lưới cực hiểm hóc!");
            } else if (saved) {
                alert("❌ CẢN PHÁ! Thủ môn đã bay người đẩy bóng thành công!");
            } else {
                alert("OUT! Cú sút đi ra ngoài khung thành!");
            }

            document.getElementById('scoreInfo').innerText = `Bàn thắng: ${score} | Lượt: ${attempts}`;
            
            setTimeout(() => {
                ball.position.set(0, 0.22, 3.2);
                keeperGroup.position.set(0, 0, -5.7);
                keeperGroup.position.y = 0;
                keeperGroup.rotation.z = 0;
                if(rightLegMesh) rightLegMesh.rotation.x = 0;
                buildStrikerMesh();
                kickProgress = 0;
                isTargeting = false;
                gameState = 'AIM';
            }, 800);
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
