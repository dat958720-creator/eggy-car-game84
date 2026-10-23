import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Eggy Car - Từ Từ Rớt Trứng",
    page_icon="🥚",
    layout="centered"
)

st.title("🥚 Eggy Car - Cân Bằng & Tốc Độ")
st.markdown("""
* **Điều khiển**: Dùng phím **Mũi tên Phải (👉) / D** để tăng tốc, **Mũi tên Trải (👈) / A** để lùi/phanh.
* **Luật chơi**: Xe chạy nhanh mạnh mẽ. Nếu bạn liên tục phóng bạt mạng qua dốc không giảm tốc, quả trứng sẽ **từ từ chao đảo, văng ra rồi rơi xuống đất** mới thua[cite: 1]!
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
                osc.frequency.setValueAtTime(70, audioCtx.currentTime);
                osc.frequency.linearRampToValueAtTime(110, audioCtx.currentTime + 0.05);
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
        let gameState = "MENU"; // MENU, PLAYING, GAMEOVER, VICTORY
        let currentLevel = 1;
        let targetDistance = 120;
        let distance = 0;
        let keys = {};

        // Xe chạy tốc độ cao
        let car = { x: 150, y: 260, vx: 0, ax: 0.45, maxSpeed: 13.0, wheelAngle: 0 };
        // Thêm biến instability (độ mất ổn định tích lũy dần)
        let egg = { worldX: 150, yOff: -30, vx: 0, vy: 0, angle: 0, angularVel: 0, instability: 0, isDropped: false };

        document.addEventListener("keydown", (e) => {
            initAudio();
            keys[e.key] = true;
        });
        document.addEventListener("keyup", (e) => keys[e.key] = false);

        function startLevel(level) {
            currentLevel = level;
            if (level === 1) targetDistance = 120;
            else if (level === 2) targetDistance = 220;
            else if (level === 3) targetDistance = 350;

            distance = 0;
            gameState = "PLAYING";
            car.x = 150;
            car.vx = 0;
            car.wheelAngle = 0;
            egg.worldX = 150;
            egg.yOff = -30;
            egg.vx = 0;
            egg.vy = 0;
            egg.angle = 0;
            egg.angularVel = 0;
            egg.instability = 0;
            egg.isDropped = false;
        }

        canvas.addEventListener("click", function(event) {
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;

            if (gameState === "MENU") {
                if (mouseX >= canvas.width/2 - 110 && mouseX <= canvas.width/2 + 110 && mouseY >= 170 && mouseY <= 215) startLevel(1);
                else if (mouseX >= canvas.width/2 - 110 && mouseX <= canvas.width/2 + 110 && mouseY >= 230 && mouseY <= 275) startLevel(2);
                else if (mouseX >= canvas.width/2 - 110 && mouseX <= canvas.width/2 + 110 && mouseY >= 290 && mouseY <= 335) startLevel(3);
            } 
            else if (gameState === "GAMEOVER") {
                if (mouseX >= canvas.width/2 - 110 && mouseX <= canvas.width/2 + 110 && mouseY >= 210 && mouseY <= 260) startLevel(currentLevel);
                else if (mouseX >= canvas.width/2 - 110 && mouseX <= canvas.width/2 + 110 && mouseY >= 275 && mouseY <= 325) gameState = "MENU";
            }
            else if (gameState === "VICTORY") {
                if (mouseX >= canvas.width/2 - 110 && mouseX <= canvas.width/2 + 110 && mouseY >= 230 && mouseY <= 280) {
                    if (currentLevel < 3) startLevel(currentLevel + 1);
                    else gameState = "MENU";
                }
            }
        });

        function getGroundY(x) {
            let base = 260;
            if (x < 350) return base;
            let progress = x - 350;
            if (currentLevel === 1) return base + Math.sin(progress * 0.006) * 22;
            else if (currentLevel === 2) return base + Math.sin(progress * 0.008) * 32 + Math.sin(progress * 0.02) * 12;
            else return base + Math.sin(progress * 0.01) * 42 + Math.sin(progress * 0.03) * 16;
        }

        function update() {
            if (gameState !== "PLAYING") return;

            let moving = false;
            let currentMaxSpeed = car.maxSpeed + (currentLevel - 1) * 1.5;

            if (keys["ArrowRight"] || keys["d"] || keys["D"]) {
                car.vx = Math.min(car.vx + car.ax, currentMaxSpeed);
                moving = true;
            } else if (keys["ArrowLeft"] || keys["a"] || keys["A"]) {
                car.vx = Math.max(car.vx - car.ax, -currentMaxSpeed / 1.5);
                moving = true;
            } else {
                car.vx *= 0.97;
            }

            if (moving) playEngineSound();

            if (car.vx > 0) distance += car.vx * 0.05;
            car.wheelAngle += car.vx * 0.1;

            if (distance >= targetDistance) {
                gameState = "VICTORY";
                return;
            }

            let screenX = 220;
            let currentCarWorldX = screenX + distance;
            car.y = getGroundY(currentCarWorldX);

            if (egg.isDropped) {
                egg.vy += 0.55; 
                egg.yOff += egg.vy;
                egg.worldX += egg.vx;
                egg.angle += 0.15;

                let groundAtEgg = getGroundY(egg.worldX);
                if (car.y + egg.yOff >= groundAtEgg) {
                    gameState = "GAMEOVER";
                    playEggCrackSound();
                }
            } else {
                egg.worldX = currentCarWorldX;
                
                let slopeEffect = Math.abs(getGroundY(currentCarWorldX + 5) - getGroundY(currentCarWorldX - 5));
                
                // Cơ chế TỪ TỪ RỚT: Tích lũy độ mất ổn định khi xe chạy quá nhanh qua chỗ xóc
                if (Math.abs(car.vx) > 9 && slopeEffect > 1.2) {
                    egg.instability += 0.025; // Tăng dần độ chao đảo theo thời gian chịu xóc
                } else {
                    egg.instability = Math.max(0, egg.instability - 0.015); // Hồi phục dần nếu đi êm
                }

                egg.angularVel += (-car.vx * 0.01) + (Math.sin(Date.now() * 0.02) * egg.instability * 0.1); 
                egg.angularVel -= egg.angle * 0.05; 
                egg.angularVel *= 0.88; 
                egg.angle += egg.angularVel;

                // Khi độ mất ổn định tích lũy đủ lớn (chạy nhanh xóc nảy lâu), trứng mới văng ra từ từ
                if (egg.instability > 1.5 || Math.abs(egg.angle) > 2.2) {
                    egg.isDropped = true;
                    egg.vy = -3.5; 
                    egg.vx = car.vx * 0.6; 
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Mặt Trời Vàng Rực
            ctx.fillStyle = "#f39c12";
            ctx.beginPath();
            ctx.arc(220, 80, 55, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(220, 80, 46, 0, Math.PI * 2);
            ctx.fill();

            // 2. Dãy Núi Phía Xa
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

            // 3. Cây Cối Xanh
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

            // 4. Mặt Đường & Lòng Đất Đỏ
            let screenX = 220;

            ctx.beginPath();
            ctx.moveTo(0, canvas.height);
            for (let px = 0; px <= canvas.width; px += 10) {
                let worldXCoord = px + distance;
                let gy = getGroundY(worldXCoord);
                ctx.lineTo(px, gy);
            }
            ctx.lineTo(canvas.width, canvas.height);
            ctx.fillStyle = "#c0392b"; 
            ctx.fill();

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

            // 5. Xe Jeep Đỏ & Giỏ Trứng
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

            if (gameState === "PLAYING") {
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 15px Arial";
                ctx.textAlign = "center";
                ctx.fillText(Math.floor(distance) + "m / " + targetDistance + "m", screenX, car.y + 6);
            }

            // 6. Bánh Xe
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

            // 7. Quả Trứng Có Mặt Cười
            ctx.save();
            let eggScreenX = egg.isDropped ? (screenX + (egg.worldX - (screenX + distance))) : screenX;
            let currentCarY = getGroundY(egg.isDropped ? egg.worldX : (screenX + distance));
            ctx.translate(eggScreenX, currentCarY + egg.yOff);
            ctx.rotate(egg.angle);

            if (gameState !== "GAMEOVER") {
                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.ellipse(0, 0, 13, 18, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#bdc3c7";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                ctx.fillStyle = "#2c3e50";
                ctx.beginPath();
                ctx.arc(-4, -3, 2, 0, Math.PI * 2); 
                ctx.arc(4, -3, 2, 0, Math.PI * 2);  
                ctx.fill();
                ctx.beginPath();
                ctx.arc(0, 2, 5, 0, Math.PI, false);
                ctx.stroke();
            } else {
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

            // 8. MÀN HÌNH MENU
            if (gameState === "MENU") {
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "900 32px 'Arial Black', sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("CHỌN MÀN CHƠI", canvas.width / 2, 110);

                ctx.fillStyle = "#3498db";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 170, 220, 45, 22);
                ctx.fill();
                ctx.strokeStyle = "#fff"; ctx.lineWidth = 3; ctx.stroke();
                ctx.fillStyle = "#fff"; ctx.font = "bold 16px Arial";
                ctx.fillText("⭐ MÀN 1 (120m)", canvas.width / 2, 198);

                ctx.fillStyle = "#f39c12";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 230, 220, 45, 22);
                ctx.fill();
                ctx.stroke();
                ctx.fillText("⭐⭐ MÀN 2 (220m)", canvas.width / 2, 258);

                ctx.fillStyle = "#e74c3c";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 290, 220, 45, 22);
                ctx.fill();
                ctx.stroke();
                ctx.fillText("⭐⭐⭐ MÀN 3 (350m)", canvas.width / 2, 318);
            }

            // 9. MÀN HÌNH GAMEOVER
            if (gameState === "GAMEOVER") {
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "900 30px 'Arial Black', sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("TRỨNG ĐÃ VỠ!", canvas.width / 2, 120);

                ctx.fillStyle = "#f1c40f";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 210, 220, 50, 25);
                ctx.fill();
                ctx.strokeStyle = "#fff"; ctx.lineWidth = 3; ctx.stroke();
                ctx.fillStyle = "#fff"; ctx.font = "bold 16px Arial";
                ctx.fillText("🔄 THỬ LẠI", canvas.width / 2, 242);

                ctx.fillStyle = "#2ecc71";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 275, 220, 50, 25);
                ctx.fill();
                ctx.stroke();
                ctx.fillText("🏠 CHỌN MÀN", canvas.width / 2, 307);
            }

            // 10. MÀN HÌNH CHIẾN THẮNG
            if (gameState === "VICTORY") {
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#f1c40f";
                ctx.font = "900 32px 'Arial Black', sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("CHIẾN THẮNG!", canvas.width / 2, 120);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 18px Arial";
                ctx.fillText("Bạn đã hoàn thành Màn " + currentLevel + " xuất sắc!", canvas.width / 2, 170);

                ctx.fillStyle = "#2ecc71";
                ctx.beginPath();
                ctx.roundRect(canvas.width/2 - 110, 230, 220, 50, 25);
                ctx.fill();
                ctx.strokeStyle = "#fff"; ctx.lineWidth = 3; ctx.stroke();
                ctx.fillStyle = "#fff"; ctx.font = "bold 16px Arial";
                let btnText = currentLevel < 3 ? "⏩ MÀN TIẾP THEO" : "🏠 HOÀN TẤT";
                ctx.fillText(btnText, canvas.width / 2, 262);
            }

            ctx.textAlign = "left";
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
