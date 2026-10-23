import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Eggy Car - Chỉ Thua Khi Trứng Chạm Đất",
    page_icon="🥚",
    layout="centered"
)

st.title("🥚 Eggy Car - Rớt Xuống Đất Mới Thua")
st.markdown("""
* **Điều khiển**: Dùng phím **Mũi tên Phải (👉) / D** để tiến, **Mũi tên Trái (👈) / A** để lùi.
* **Luật chơi**: Quả trứng văng khỏi xe cứ để nó bay, **chừng nào nó rơi chạm xuống mặt đất** thì game mới thực sự thua!
""")

eggy_car_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; padding: 0; background-color: #111; text-align: center; color: white; font-family: 'Arial Black', Arial, sans-serif; user-select: none; }
        .game-container { position: relative; display: inline-block; margin-top: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.8); border-radius: 12px; overflow: hidden; }
        canvas { display: block; background: linear-gradient(to bottom, #1e528e 0%, #3a7bd5 40%, #6dd5ed 100%); }
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
                osc.frequency.linearRampToValueAtTime(95, audioCtx.currentTime + 0.05);
                gain.gain.setValueAtTime(0.025, audioCtx.currentTime);
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

        let car = { x: 150, y: 220, vx: 0, ax: 0.28, maxSpeed: 9.5, wheelAngle: 0 };
        // Quản lý vị trí quả trứng (worldX và worldY để khi văng ra nó rơi theo không gian thực)
        let egg = { worldX: 150, yOff: -32, vx: 0, vy: 0, angle: 0, angularVel: 0, isDropped: false };

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
            egg.yOff = -32;
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

        function getGroundY(x) {
            return 240 + Math.sin(x * 0.008) * 15 + Math.cos(x * 0.02) * 5;
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
                // Trứng rơi tự do theo trọng lực
                egg.vy += 0.55; // Trọng lực kéo xuống
                egg.yOff += egg.vy;
                egg.worldX += egg.vx;
                egg.angle += egg.angularVel;

                let groundAtEgg = getGroundY(egg.worldX);

                // CHỈ KHI TRỨNG RƠI CHẠM ĐẤT THÌ MỚI GAME OVER THẬT SỰ
                if (car.y + egg.yOff >= groundAtEgg) {
                    gameOver = true;
                    playEggCrackSound();
                }
            } else {
                // Trứng nằm trên xe
                egg.worldX = currentCarWorldX;
                egg.angularVel += (-car.vx * 0.018); 
                egg.angularVel -= egg.angle * 0.015; 
                egg.angularVel *= 0.93; 
                egg.angle += egg.angularVel;

                // Nếu lắc lư quá đà (nghiêng quá 2.2), trứng văng ra khỏi giỏ xe
                if (Math.abs(egg.angle) > 2.2) {
                    egg.isDropped = true;
                    egg.vy = -3.0; // Bật văng lên không trung trước khi rơi
                    egg.vx = car.vx * 0.8; // Bay theo đà quán tính của xe
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Mặt Trời Vàng Rực
            ctx.fillStyle = "#f39c12";
            ctx.beginPath();
            ctx.arc(160, 70, 50, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(160, 70, 42, 0, Math.PI * 2);
            ctx.fill();

            // 2. Dãy Núi Phía Xa
            ctx.fillStyle = "#52be80";
            ctx.beginPath();
            ctx.moveTo(0, 260);
            ctx.lineTo(150, 140);
            ctx.lineTo(320, 260);
            ctx.lineTo(500, 120);
            ctx.lineTo(680, 260);
            ctx.lineTo(750, 180);
            ctx.lineTo(750, 350);
            ctx.lineTo(0, 350);
            ctx.fill();

            // 3. Cây Cối
            function drawTree(tx, ty) {
                ctx.fillStyle = "#1e8449";
                ctx.beginPath();
                ctx.moveTo(tx, ty - 50);
                ctx.lineTo(tx - 18, ty);
                ctx.lineTo(tx + 18, ty);
                ctx.fill();
                ctx.fillStyle = "#7e5109";
                ctx.fillRect(tx - 3, ty, 6, 12);
            }
            drawTree(100, 230);
            drawTree(280, 220);
            drawTree(600, 210);

            // 4. Mặt Đường & Lòng Đất
            let screenX = 220;
            let groundY = car.y;

            ctx.fillStyle = "#e5e8e8";
            ctx.fillRect(0, groundY + 20, canvas.width, 16);

            ctx.fillStyle = "#b03a2e";
            ctx.fillRect(0, groundY + 36, canvas.width, 180);

            // Hạt Đốm Đất Đỏ
            ctx.fillStyle = "#78281f";
            for (let i = 20; i < canvas.width; i += 50) {
                let shift = (distance * 15) % 50;
                ctx.beginPath();
                ctx.arc(i - shift, groundY + 60, 3.5, 0, Math.PI * 2);
                ctx.arc(i + 20 - shift, groundY + 90, 4, 0, Math.PI * 2);
                ctx.arc(i + 35 - shift, groundY + 120, 3, 0, Math.PI * 2);
                ctx.fill();
            }

            // 5. Xe Jeep Đỏ & Thanh Giỏ Trứng
            ctx.strokeStyle = "#17202a";
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.moveTo(screenX - 22, car.y - 10); ctx.lineTo(screenX - 22, car.y - 38);
            ctx.moveTo(screenX + 22, car.y - 10); ctx.lineTo(screenX + 22, car.y - 38);
            ctx.stroke();

            ctx.fillStyle = "#e74c3c";
            ctx.beginPath();
            ctx.roundRect(screenX - 42, car.y - 12, 84, 26, 6);
            ctx.fill();

            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(screenX + 38, car.y - 2, 4.5, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 15px Arial";
            ctx.textAlign = "center";
            ctx.fillText(Math.floor(distance) + "m", screenX, car.y + 6);

            // 6. Bánh Xe
            function drawWheel(wx, wy) {
                ctx.save();
                ctx.translate(wx, wy);
                ctx.rotate(car.wheelAngle);
                ctx.fillStyle = "#1b2631";
                ctx.beginPath();
                ctx.arc(0, 0, 15, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#eaeded";
                ctx.beginPath();
                ctx.arc(0, 0, 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            drawWheel(screenX - 26, car.y + 16);
            drawWheel(screenX + 26, car.y + 16);

            // 7. Quả Trứng (Hiển thị theo tọa độ thực tế trên màn hình)
            ctx.save();
            let eggScreenX = egg.isDropped ? (screenX + (egg.worldX - (screenX + distance))) : screenX;
            ctx.translate(eggScreenX, car.y + egg.yOff);
            ctx.rotate(egg.angle);

            if (!gameOver) {
                ctx.fillStyle = "#fffdf0";
                ctx.beginPath();
                ctx.ellipse(0, -2, 12, 17, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#d5dbdb";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                ctx.fillStyle = "rgba(255,255,255,0.8)";
                ctx.beginPath();
                ctx.ellipse(-3, -7, 3, 5, -0.3, 0, Math.PI * 2);
                ctx.fill();
            } else {
                // Trứng vỡ bẹp trên mặt đất
                ctx.fillStyle = "#f1c40f";
                ctx.beginPath();
                ctx.ellipse(0, 5, 14, 6, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.arc(-4, 3, 3, 0, Math.PI * 2);
                ctx.arc(6, 4, 2.5, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();

            // 8. Màn hình Game Over "Get another chance"[cite: 1]
            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.65)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "900 30px 'Arial Black', sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "black";
                ctx.shadowBlur = 6;
                ctx.fillText("Get another chance", canvas.width / 2, 120);
                ctx.shadowBlur = 0;

                // Nút 1: WATCH AD TO RESUME
                ctx.fillStyle = "#f39c12";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 100, 180, 200, 40, 20);
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px Arial";
                ctx.fillText("📹 WATCH AD TO RESUME", canvas.width / 2, 205);

                // Nút 2: REPLAY
                ctx.fillStyle = "#f1c40f";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 100, 235, 200, 40, 20);
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 15px Arial";
                ctx.fillText("🔄 REPLAY", canvas.width / 2, 260);

                // Nút 3: HOME
                ctx.fillStyle = "#2ecc71";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 100, 290, 200, 40, 20);
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 15px Arial";
                ctx.fillText("🏠 HOME", canvas.width / 2, 315);

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
