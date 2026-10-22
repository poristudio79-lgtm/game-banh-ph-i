import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="World Cup 3D Shootout", page_icon="🏆", layout="wide")

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
    #gameContainer { position: relative; width: 920px; height: 580px; background: #111; border-radius: 12px; overflow: hidden; border: 3px solid #333; }
    canvas { display: block; width: 100%; height: 100%; }
    
    .screen { position: absolute; inset: 0; background: rgba(10, 15, 30, 0.95); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 100; transition: all 0.3s ease; }
    .hidden { display: none !important; opacity: 0; pointer-events: none; }
    
    h1 { font-size: 36px; margin-bottom: 20px; color: #ffeb3b; text-shadow: 0 0 15px rgba(255,235,59,0.5); letter-spacing: 2px; }
    h2 { font-size: 22px; margin-bottom: 12px; color: #00e676; }
    
    .btn-play { width: 260px; height: 65px; background: linear-gradient(135deg, #ff9800, #ff5722); border: none; border-radius: 12px; color: #fff; font-size: 26px; font-weight: bold; cursor: pointer; box-shadow: 0 6px 20px rgba(255,152,0,0.5); transition: transform 0.2s, box-shadow 0.2s; display: flex; align-items: center; justify-content: center; letter-spacing: 1.5px; z-index: 101; }
    .btn-play:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 10px 25px rgba(255,152,0,0.7); }

    /* LƯỚI 20 QUỐC GIA (5 CỘT x 4 HÀNG) */
    .country-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; width: 94%; max-width: 860px; height: 420px; overflow-y: auto; padding-right: 5px; }
    .country-grid::-webkit-scrollbar { width: 6px; }
    .country-grid::-webkit-scrollbar-thumb { background: #ffeb3b; border-radius: 3px; }
    
    .country-card { background: rgba(255,255,255,0.08); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 10px 4px; text-align: center; cursor: pointer; transition: all 0.2s; z-index: 101; }
    .country-card:hover { border-color: #ffeb3b; background: rgba(255,235,59,0.2); transform: translateY(-3px); }
    .country-flag { font-size: 28px; margin-bottom: 2px; }
    .country-name { font-size: 13px; font-weight: bold; color: #ffeb3b; }
    .player-star { font-size: 11px; color: #ddd; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    #hud { position: absolute; top: 15px; left: 20px; right: 20px; display: flex; justify-content: space-between; font-size: 16px; font-weight: bold; z-index: 5; pointer-events: none; }
    .badge { background: rgba(0,0,0,0.6); padding: 8px 15px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

<div id="gameContainer">
    <div id="hud">
        <div class="badge" id="playerInfo">🏆 Quốc gia: -</div>
        <div class="badge" id="scoreInfo">Bàn thắng: 0 | Lượt: 0</div>
    </div>

    <!-- MENU CHÍNH WORLD CUP -->
    <div id="menuScreen" class="screen">
        <h1>🏆 WORLD CUP 2026</h1>
        <button id="playBtn" class="btn-play">WORLD CUP</button>
    </div>

    <!-- CHỌN 20 QUỐC GIA & SIÊU SAO ĐẠI DIỆN -->
    <div id="selectScreen" class="screen hidden">
        <h2>CHỌN QUỐC GIA THI ĐẤU (20 ĐỘI BÓNG)</h2>
        <div class="country-grid" id="countryGrid"></div>
    </div>
</div>

<script>
// DANH SÁCH 20 QUỐC GIA VÀ SIÊU SAO ĐẠI DIỆN NỔI TIẾNG NHẤT
const COUNTRIES = [
    { country: "Việt Nam 🇻🇳", flag: "🇻🇳", player: "Quang Hải", jersey: 19, shirtColor: 0xda251d, skinColor: 0xffdbac, hairColor: 0x111111 },
    { country: "Pháp 🇫🇷", flag: "🇫🇷", player: "K. Mbappé", jersey: 10, shirtColor: 0x002395, skinColor: 0x8d5524, hairColor: 0x111111 },
    { country: "Argentina 🇦🇷", flag: "🇦🇷", player: "L. Messi", jersey: 10, shirtColor: 0x75aadb, skinColor: 0xffdbac, hairColor: 0x3b2219 },
    { country: "Bồ Đào Nha 🇵🇹", flag: "🇵🇹", player: "C. Ronaldo", jersey: 7, shirtColor: 0xda291c, skinColor: 0xe0ac69, hairColor: 0x111111 },
    { country: "Tây Ban Nha 🇪🇸", flag: "🇪🇸", player: "Lamine Yamal", jersey: 19, shirtColor: 0xaa151b, skinColor: 0x8d5524, hairColor: 0x111111 },
    { country: "Na Uy 🇳🇴", flag: "🇳🇴", player: "E. Haaland", jersey: 9, shirtColor: 0xba0c2f, skinColor: 0xffdbac, hairColor: 0xf3e5ab },
    { country: "Brazil 🇧🇷", flag: "🇧🇷", player: "Vinícius Jr.", jersey: 7, shirtColor: 0xffdc02, skinColor: 0x5c3826, hairColor: 0x111111 },
    { country: "Anh 🏴󠁧󠁢󠁥󠁮󠁧󠁿", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿", player: "Harry Kane", jersey: 9, shirtColor: 0xffffff, skinColor: 0xffdbac, hairColor: 0xd4af37 },
    { country: "Đức 🇩🇪", flag: "🇩🇪", player: "J. Musiala", jersey: 10, shirtColor: 0xffffff, skinColor: 0x8d5524, hairColor: 0x111111 },
    { country: "Ai Cập 🇪🇬", flag: "🇪🇬", player: "M. Salah", jersey: 11, shirtColor: 0xc8102e, skinColor: 0x8d5524, hairColor: 0x221100 },
    { country: "Hàn Quốc 🇰🇷", flag: "🇰🇷", player: "Son Heung-min", jersey: 7, shirtColor: 0xeb1c24, skinColor: 0xffdbac, hairColor: 0x111111 },
    { country: "Nhật Bản 🇯🇵", flag: "🇯🇵", player: "K. Mitoma", jersey: 7, shirtColor: 0x000080, skinColor: 0xffdbac, hairColor: 0x111111 },
    { country: "Bỉ 🇧🇪", flag: "🇧🇪", player: "K. De Bruyne", jersey: 7, shirtColor: 0xe30613, skinColor: 0xffdbac, hairColor: 0xeecc88 },
    { country: "Ý 🇮🇹", flag: "🇮🇹", player: "F. Chiesa", jersey: 14, shirtColor: 0x0066bc, skinColor: 0xffdbac, hairColor: 0x3b2219 },
    { country: "Hà Lan 🇳🇱", flag: "🇳🇱", player: "V. van Dijk", jersey: 4, shirtColor: 0xff6600, skinColor: 0x8d5524, hairColor: 0x111111 },
    { country: "Croatia 🇭🇷", flag: "🇭🇷", player: "L. Modrić", jersey: 10, shirtColor: 0xff0000, skinColor: 0xffdbac, hairColor: 0xeecc88 },
    { country: "Uruguay 🇺🇾", flag: "🇺🇾", player: "F. Valverde", jersey: 15, shirtColor: 0x5cbbf2, skinColor: 0xffdbac, hairColor: 0x3b2219 },
    { country: "Ma-rốc 🇲🇦", flag: "🇲🇦", player: "A. Hakimi", jersey: 2, shirtColor: 0xc1272d, skinColor: 0x8d5524, hairColor: 0x111111 },
    { country: "Mỹ 🇺🇸", flag: "🇺🇸", player: "C. Pulisic", jersey: 10, shirtColor: 0xffffff, skinColor: 0xffdbac, hairColor: 0x3b2219 },
    { country: "Mexico 🇲🇽", flag: "🇲🇽", player: "E. Álvarez", jersey: 4, shirtColor: 0x006847, skinColor: 0xe0ac69, hairColor: 0x111111 }
];

let selectedCountry = null;
let score = 0, attempts = 0;
let gameState = 'MENU';

document.getElementById('playBtn').addEventListener('click', function(e) {
    e.stopPropagation();
    document.getElementById('menuScreen').classList.add('hidden');
    document.getElementById('selectScreen').classList.remove('hidden');
    initCountryGrid();
});

function initCountryGrid() {
    const grid = document.getElementById('countryGrid');
    grid.innerHTML = '';
    COUNTRIES.forEach(c => {
        const card = document.createElement('div');
        card.className = 'country-card';
        card.onclick = (e) => {
            e.stopPropagation();
            selectCountry(c);
        };
        card.innerHTML = `
            <div class="country-flag">${c.flag}</div>
            <div class="country-name">${c.country.split(' ')[0]}</div>
            <div class="player-star">⭐ ${c.player}</div>
        `;
        grid.appendChild(card);
    });
}

function selectCountry(item) {
    selectedCountry = item;
    document.getElementById('selectScreen').classList.add('hidden');
    document.getElementById('playerInfo').innerText = `${item.flag} ${item.country.split(' ')[0]} - ${item.player}`;
    buildStrikerMesh();
    setTimeout(() => { gameState = 'AIM'; }, 200);
}

// SETUP THREE.JS 3D SCENE
const container = document.getElementById('gameContainer');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1329);
scene.fog = new THREE.Fog(0x0b1329, 15, 35);

const camera = new THREE.PerspectiveCamera(50, 920 / 580, 0.1, 1000);
camera.position.set(0, 3.2, 8.8);
camera.lookAt(0, 1.4, -2);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(920, 580);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.7); scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.9); dirLight.position.set(5, 12, 5); dirLight.castShadow = true; scene.add(dirLight);

// SÂN CỎ
const pitchGeo = new THREE.PlaneGeometry(18, 22);
const pitchMat = new THREE.MeshStandardMaterial({ color: 0x1e7e34, roughness: 0.8 });
const pitch = new THREE.Mesh(pitchGeo, pitchMat); pitch.rotation.x = -Math.PI / 2; pitch.receiveShadow = true; scene.add(pitch);

// KHÁN ĐÀI HÀNG GHẾ KHÁN GIẢ
const stadiumGroup = new THREE.Group();
const fans = [];
const crowdColors = [0xe74c3c, 0x3498db, 0xf1c40f, 0x2ecc71, 0x9b59b6, 0xffffff];

function buildBleachers(side) {
    const bleacherGroup = new THREE.Group();
    const rows = 4;
    const standMat = new THREE.MeshStandardMaterial({ color: 0x2a2e39, roughness: 0.7 });
    const seatMat = new THREE.MeshStandardMaterial({ color: 0x0070f3, roughness: 0.5 });

    for(let r = 0; r < rows; r++) {
        const stepGeo = new THREE.BoxGeometry(0.8, 0.4 + r*0.4, 14);
        const step = new THREE.Mesh(stepGeo, standMat);
        step.position.set(side * (7.5 + r*0.75), (0.2 + r*0.2), -2);
        bleacherGroup.add(step);

        for(let z = -7; z <= 3; z += 1.1) {
            const seatGeo = new THREE.BoxGeometry(0.4, 0.1, 0.8);
            const seat = new THREE.Mesh(seatGeo, seatMat);
            seat.position.set(side * (7.5 + r*0.75), 0.45 + r*0.4, z);
            bleacherGroup.add(seat);

            if(Math.random() > 0.15) {
                const fanGeo = new THREE.BoxGeometry(0.3, 0.6, 0.3);
                const fanMat = new THREE.MeshBasicMaterial({ color: crowdColors[Math.floor(Math.random()*crowdColors.length)] });
                const fan = new THREE.Mesh(fanGeo, fanMat);
                fan.position.set(side * (7.5 + r*0.75), 0.8 + r*0.4, z);
                fan.userData = { initialY: fan.position.y, speed: 0.05 + Math.random()*0.08, offset: Math.random()*Math.PI*2 };
                bleacherGroup.add(fan);
                fans.push(fan);
            }
        }
    }
    stadiumGroup.add(bleacherGroup);
}
buildBleachers(1); buildBleachers(-1);
scene.add(stadiumGroup);

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

// TÂM NGẮM 3D
const aimGroup = new THREE.Group();
const ringGeo = new THREE.RingGeometry(0.2, 0.26, 32);
const ringMat = new THREE.MeshBasicMaterial({ color: 0x00ffcc, side: THREE.DoubleSide });
const aimRing = new THREE.Mesh(ringGeo, ringMat);
const dotGeo = new THREE.CircleGeometry(0.05, 16);
const dotMat = new THREE.MeshBasicMaterial({ color: 0xffeb3b, side: THREE.DoubleSide });
const aimDot = new THREE.Mesh(dotGeo, dotMat);
aimGroup.add(aimRing, aimDot);
aimGroup.position.set(0, 1.3, -5.9);
scene.add(aimGroup);

// QUẢ BÓNG 3D
const ballGeo = new THREE.SphereGeometry(0.22, 24, 24);
const ballMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
const ball = new THREE.Mesh(ballGeo, ballMat);
ball.position.set(0, 0.22, 3.2);
ball.castShadow = true;
scene.add(ball);

// THỦ MÔN
const keeperGroup = new THREE.Group();
const keeperBodyMat = new THREE.MeshStandardMaterial({ color: 0xffeb3b });
const keeperSkinMat = new THREE.MeshStandardMaterial({ color: 0xffdbac });
const keeperPantMat = new THREE.MeshStandardMaterial({ color: 0x222222 });

const keeperBody = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.9, 0.3), keeperBodyMat); keeperBody.position.y = 1.15;
const keeperHead = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 16), keeperSkinMat); keeperHead.position.y = 1.8;

const armGeo = new THREE.BoxGeometry(0.18, 0.7, 0.18);
const keeperLeftArm = new THREE.Mesh(armGeo, keeperSkinMat); keeperLeftArm.position.set(-0.45, 1.1, 0); keeperLeftArm.rotation.z = 0.3;
const keeperRightArm = new THREE.Mesh(armGeo, keeperSkinMat); keeperRightArm.position.set(0.45, 1.1, 0); keeperRightArm.rotation.z = -0.3;

const legGeo = new THREE.BoxGeometry(0.22, 0.8, 0.22);
const keeperLeftLeg = new THREE.Mesh(legGeo, keeperPantMat); keeperLeftLeg.position.set(-0.2, 0.4, 0);
const keeperRightLeg = new THREE.Mesh(legGeo, keeperPantMat); keeperRightLeg.position.set(0.2, 0.4, 0);

keeperGroup.add(keeperBody, keeperHead, keeperLeftArm, keeperRightArm, keeperLeftLeg, keeperRightLeg);
keeperGroup.position.set(0, 0, -5.7);
scene.add(keeperGroup);

// CẦU THỦ ĐẠI DIỆN QUỐC GIA
let strikerGroup = new THREE.Group();
let rightLegMesh = null;
scene.add(strikerGroup);

function buildStrikerMesh() {
    while(strikerGroup.children.length > 0){ strikerGroup.remove(strikerGroup.children[0]); }
    if (!selectedCountry) return;

    const mat = new THREE.MeshStandardMaterial({ color: selectedCountry.shirtColor });
    const skinMat = new THREE.MeshStandardMaterial({ color: selectedCountry.skinColor });
    const hairMat = new THREE.MeshStandardMaterial({ color: selectedCountry.hairColor });

    const body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.0, 0.3), mat); body.position.y = 1.1; body.castShadow = true;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), skinMat); head.position.y = 1.85;
    const hair = new THREE.Mesh(new THREE.SphereGeometry(0.23, 16, 16), hairMat); hair.position.set(0, 1.92, -0.03); hair.scale.set(1, 0.7, 1.1);

    const armGeo = new THREE.BoxGeometry(0.18, 0.7, 0.18);
    const leftArm = new THREE.Mesh(armGeo, skinMat); leftArm.position.set(-0.42, 1.1, 0);
    const rightArm = new THREE.Mesh(armGeo, skinMat); rightArm.position.set(0.42, 1.1, 0);

    const legGeo = new THREE.BoxGeometry(0.2, 0.9, 0.2);
    const leftLeg = new THREE.Mesh(legGeo, skinMat); leftLeg.position.set(-0.2, 0.45, 0);
    rightLegMesh = new THREE.Mesh(legGeo, skinMat); rightLegMesh.position.set(0.2, 0.45, 0);

    strikerGroup.add(body, head, hair, leftArm, rightArm, leftLeg, rightLegMesh);
    
    strikerGroup.position.set(-1.2, 0, 3.8);
    strikerGroup.rotation.y = 0.45; 
}

let targetAim = { x: 0, y: 1.3 };
let isTargeting = false;

container.addEventListener('mousemove', (e) => {
    if (gameState !== 'AIM') return;
    const rect = container.getBoundingClientRect();
    
    let mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    let mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    
    targetAim.x = mouseX * 3.2; 
    targetAim.y = Math.max(0.2, Math.min(2.8, mouseY * 1.8 + 1.4)); 
    
    aimGroup.position.x = targetAim.x;
    aimGroup.position.y = targetAim.y;
    aimGroup.visible = true;
    isTargeting = true;
});

container.addEventListener('click', () => {
    if (gameState === 'AIM' && isTargeting) {
        gameState = 'KICKING';
        aimGroup.visible = false;
    }
});

let kickProgress = 0;
let keeperTargetX = 0, keeperTargetY = 1.1;
let ballSpeedX = 0, ballSpeedY = 0, ballSpeedZ = 0;

let clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    let time = clock.getElapsedTime();

    if (aimGroup.visible) {
        aimRing.rotation.z += 0.03;
        let scale = 1 + Math.sin(time * 6) * 0.1;
        aimGroup.scale.set(scale, scale, scale);
    }

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
                alert(`⚽ VÀOOOOOO! Bàn thắng quý như vàng cho ${selectedCountry.country}!`);
            } else if (saved) {
                alert("❌ CẢN PHÁ! Thủ môn đã xuất sắc cản phá!");
            } else {
                alert("OUT! Cú sút không trúng khung thành!");
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
                aimGroup.visible = true;
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

components.html(GAME_3D_HTML, height=600)
