import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Eggy Car - Giống Bản Gốc",
    page_icon="🥚",
    layout="centered"
)

st.title("🥚 Eggy Car - Phiên Bản Chuẩn Xác")
st.markdown("""
* **Điều khiển**: Dùng phím **Mũi tên Phải (👉) / D** để tăng tốc, **Mũi tên Trái (👈) / A** để lùi/phanh.
* **Luật chơi**: Lái xe vượt qua các đoạn dốc gồ ghề, giữ không để quả trứng văng ra khỏi xe và rơi xuống đất[cite: 2]!
""")

eggy_car_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; padding: 0; background-color: #111; text-align: center; color: white; font-family: 'Arial Black', Arial, sans-serif; user-select: none; }
        .game-container { position: relative; display: inline-block; margin-top: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.8); border-radius: 12px; overflow: hidden; }
        canvas { display: block; background: linear-gradient(to bottom, #4a90e2 0%, #a1c4fd 100%); }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas" width="750" height="420"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // --- ÂM THANH WEB AUDIO API ---
        let audioCtx = null;
        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
        }

        function playEngineSound() {
            if (!audioCtx) return;
            try {
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(60, audioCtx.currentTime);
                osc.frequency.linearRampToValueAtTime(90, audioCtx.currentTime + 0.05);
                gain.gain.setValueAtTime(0.02, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.07);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.07);
            } catch(e) {}
        }

        function playEggCrackSound() {
            if (!audioCtx) return;
            try {
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(220, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.3);
                gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.3);
            } catch(e) {}
        }

        // --- TRẠNG THÁI GAME ---
        let distance = 0;
        let gameOver = false;
        let keys = {};

        let car = { x: 150, y: 220, vx: 0, ax: 0.25, maxSpeed: 8.5, wheelAngle: 0 };
        // Trạng thái quả trứng (có mặt cười)[cite: 2]
        let egg = { worldX: 150, yOff: -30, vx: 0, vy: 0, angle: 0, angularVel: 0, isDropped: false };

        document.addEventListener("keydown", (e) => {
            initAudio();
            keys[e.key] = true;
        });
        document.addEventListener("keyup", (e) => keys[e.key] = false);

        function resetGame() {
            distance = 0;
            gameOver = false;
            car.x = 150;
            car.vx = 0;
            car.wheelAngle = 0;
            egg.worldX = 150;
            egg.yOff = -30;
            egg.vx = 0;
            egg.vy = 0;
            egg.angle = 0;
            egg.angularVel = 0;
            egg.isDropped = false;
        }

        // Tương tác bấm nút trên màn hình Game Over
        canvas.addEventListener("click", function(event) {
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;

            if (gameOver) {
                if (mouseX >= canvas.width/2 - 100 && mouseX <= canvas.width/2 + 100 && mouseY >= 180 && mouseY <= 220) {
                    resetGame(); // Resume
                }
                else if (mouseX >= canvas.width/2 - 100 && mouseX <= canvas.width/2 + 100 && mouseY >= 235 && mouseY <= 275) {
                    resetGame(); // Replay
                }
                else if (mouseX >= canvas.width/2 - 100 && mouseX <= canvas.width/2 + 100 && mouseY >= 290 && mouseY <= 330) {
                    resetGame(); // Home
                }
            }
        });

        // ĐỊA HÌNH GIỐNG ẢNH MẪU: Có các đồi nhấp nhô mượt mà
        function getGroundY(x) {
            return 260 + Math.sin(x * 0.007) * 35 + Math.sin(x * 0.02) * 12;
        }

        function update() {
            if (gameOver) return;

            let moving = false;
            if (keys["ArrowRight"] || keys["d"] || keys["D"]) {
                car.vx = Math.min(car.vx + car.ax, car.maxSpeed);
                moving = true;
            } else if (keys["ArrowLeft"] || keys["a"] || keys["A"]) {
                car.vx = Math.max(car.vx - car.ax, -car.maxSpeed / 1.5);
                moving = true;
            } else {
                car.vx *= 0.97;
            }

            if (moving) playEngineSound();

            if (car.vx > 0) distance += car.vx * 0.05;
            car.wheelAngle += car.vx * 0.1;

            let screenX = 220;
            let currentCarWorldX = screenX + distance;
            car.y = getGroundY(currentCarWorldX);

            if (egg.isDropped) {
                // Trứng rơi tự do xuống đất khi văng khỏi xe
                egg.vy += 0.5; 
                egg.yOff += egg.vy;
                egg.worldX += egg.vx;
                egg.angle += 0.1;

                let groundAtEgg = getGroundY(egg.worldX);

                // CHỈ KHI TRỨNG CHẠM ĐẤT THÌ THUA THẬT SỰ
                if (car.y + egg.yOff >= groundAtEgg) {
                    gameOver = true;
                    playEggCrackSound();
                }
            } else {
                egg.worldX = currentCarWorldX;
                
                // Độ dốc làm trứng lắc lư
                let slopeEffect = (getGroundY(currentCarWorldX + 5) - getGroundY(currentCarWorldX - 5)) * 0.06;
                egg.angularVel += (-car.vx * 0.02) - slopeEffect; 
                egg.angularVel -= egg.angle * 0.015; 
                egg.angularVel *= 0.92; 
                egg.angle += egg.angularVel;

                // NẾU LẮC LƯ QUÁ ĐÀ (VĂNG RA KHỎI XE) THÌ KÍCH HOẠT RƠI XUỐNG ĐẤT
                if (Math.abs(egg.angle) > 1.7) {
                    egg.isDropped = true;
                    egg.vy = -3.5; 
                    egg.vx = car.vx * 0.7; 
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Mặt Trời Vàng Rực[cite: 2]
            ctx.fillStyle = "#f39c12";
            ctx.beginPath();
            ctx.arc(220, 80, 55, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(220, 80, 46, 0, Math.PI * 2);
            ctx.fill();

            // 2. Dãy Núi Phía Xa[cite: 2]
            ctx.fillStyle = "#6ab04c";
            ctx.beginPath();
            ctx.moveTo(0, 280);
            ctx.lineTo(130, 160);
            ctx.lineTo(280, 280);
            ctx.lineTo(460, 140);
            ctx.lineTo(650, 280);
            ctx.lineTo(750, 200);
            ctx.lineTo(750, 400);
            ctx.lineTo(0, 400);
            ctx.fill();

            // 3. Cây Cối Xanh[cite: 2]
            function drawTree(tx, ty) {
                ctx.fillStyle = "#27ae60";
                ctx.beginPath();
                ctx.arc(tx, ty - 25, 22, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#7f8c8d";
                ctx.fillRect(tx - 3, ty - 5, 6, 20);
            }
            drawTree(120, 260);
            drawTree(350, 240);
            drawTree(620, 230);

            // 4. Mặt Đường & Lòng Đất Đỏ[cite: 2]
            let screenX = 220;

            ctx.beginPath();
            ctx.moveTo(0, canvas.height);
            for (let px = 0; px <= canvas.width; px += 10) {
                let worldXCoord = px + distance;
                let gy = getGroundY(worldXCoord);
                ctx.lineTo(px, gy);
            }
            ctx.lineTo(canvas.width, canvas.height);
            ctx.fillStyle = "#c0392b"; // Đất đỏ cam giống ảnh[cite: 2]
            ctx.fill();

            // Đường nhựa trắng xám phía trên[cite: 2]
            ctx.beginPath();
            for (let px = 0; px <= canvas.width; px += 10) {
                let worldXCoord = px + distance;
                let gy = getGroundY(worldXCoord);
                if (px === 0) ctx.moveTo(px, gy);
                else ctx.lineTo(px, gy);
            }
            ctx.lineTo(canvas.width, canvas.height);
            ctx.lineTo(0, canvas.height);
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 14;
            ctx.stroke();

            // Hạt đốm trên nền đất đỏ[cite: 2]
            ctx.fillStyle = "#962d22";
            for (let i = 20; i < canvas.width; i += 60) {
                let shift = (distance * 10) % 60;
                ctx.beginPath();
                ctx.arc(i - shift, car.y + 70, 3.5, 0, Math.PI * 2);
                ctx.arc(i + 30 - shift, car.y + 110, 4, 0, Math.PI * 2);
                ctx.fill();
            }

            // 5. Xe Jeep Đỏ & Giỏ Trứng[cite: 2]
            car.y = getGroundY(screenX + distance);

            ctx.strokeStyle = "#2c3e50";
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.moveTo(screenX - 22, car.y - 10); ctx.lineTo(screenX - 22, car.y - 35);
            ctx.moveTo(screenX + 22, car.y - 10); ctx.lineTo(screenX + 22, car.y - 35);
            ctx.stroke();

            ctx.fillStyle = "#e74c3c";
            ctx.beginPath();
            ctx.roundRect(screenX - 42, car.y - 12, 84, 26, 6);
            ctx.fill();

            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(screenX + 38, car.y - 2, 4.5, 0, Math.PI * 2);
            ctx.fill();

            // Hiển thị số mét trên xe[cite: 2]
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 15px Arial";
            ctx.textAlign = "center";
            ctx.fillText(Math.floor(distance) + "m", screenX, car.y + 6);

            // 6. Bánh Xe[cite: 2]
            function drawWheel(wx, wy) {
                ctx.save();
                ctx.translate(wx, wy);
                ctx.rotate(car.wheelAngle);
                ctx.fillStyle = "#2c3e50";
                ctx.beginPath();
                ctx.arc(0, 0, 15, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#ecf0f1";
                ctx.beginPath();
                ctx.arc(0, 0, 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            drawWheel(screenX - 26, car.y + 16);
            drawWheel(screenX + 26, car.y + 16);

            // 7. Quả Trứng Có Mặt Cười[cite: 2]
            ctx.save();
            let eggScreenX = egg.isDropped ? (screenX + (egg.worldX - (screenX + distance))) : screenX;
            let currentCarY = getGroundY(egg.isDropped ? egg.worldX : (screenX + distance));
            ctx.translate(eggScreenX, currentCarY + egg.yOff);
            ctx.rotate(egg.angle);

            if (!gameOver) {
                // Thân trứng trắng
                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.ellipse(0, 0, 13, 18, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#bdc3c7";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // Mặt cười trên quả trứng[cite: 2]
                ctx.fillStyle = "#2c3e50";
                ctx.beginPath();
                ctx.arc(-4, -3, 2, 0, Math.PI * 2); // Mắt trái
                ctx.arc(4, -3, 2, 0, Math.PI * 2);  // Mắt phải
                ctx.fill();
                // Miệng cười
                ctx.beginPath();
                ctx.arc(0, 2, 5, 0, Math.PI, false);
                ctx.stroke();
            } else {
                // Trứng vỡ bẹp trên đất
                ctx.fillStyle = "#f1c40f";
                ctx.beginPath();
                ctx.ellipse(0, 6, 14, 6, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.arc(-4, 4, 3, 0, Math.PI * 2);
                ctx.arc(6, 4, 2.5, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();

            // 8. Màn hình Game Over "Get another chance"[cite: 1]
            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "900 28px 'Arial Black', sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "black";
                ctx.shadowBlur = 6;
                ctx.fillText("Get another chance", canvas.width / 2, 110);
                ctx.shadowBlur = 0;

                // Nút 1: WATCH AD TO RESUME[cite: 1]
                ctx.fillStyle = "#f39c12";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 170, 220, 45, 22);
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 14px Arial";
                ctx.fillText("📹 WATCH AD TO RESUME", canvas.width / 2, 198);

                // Nút 2: REPLAY[cite: 1]
                ctx.fillStyle = "#f1c40f";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 230, 220, 45, 22);
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 16px Arial";
                ctx.fillText("🔄 REPLAY", canvas.width / 2, 258);

                // Nút 3: HOME[cite: 1]
                ctx.fillStyle = "#2ecc71";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 290, 220, 45, 22);
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 16px Arial";
                ctx.fillText("🏠 HOME", canvas.width / 2, 318);

                ctx.textAlign = "left";
            }
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        loop();
    </script>
</body>
</html>
"""

components.html(eggy_car_html, height=480)
