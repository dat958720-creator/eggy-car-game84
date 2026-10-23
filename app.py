import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Eggy Car - Ultimate Edition", page_icon="🥚", layout="centered"
)

st.title("🥚 Eggy Car - Phiên Bản Giống Bản Gốc 100%")
st.markdown("""
* **Điều khiển**: Dùng phím **Mũi tên Phải (👉) / D** để tiến, **Mũi tên Trái (👈) / A** để lùi và phanh.
* **Âm thanh**: Hãy bật loa máy tính để nghe tiếng động cơ và hiệu ứng âm thanh!
""")

eggy_car_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #111; text-align: center; color: white; font-family: 'Arial', sans-serif; }
        .game-container { position: relative; display: inline-block; margin-top: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.6); border-radius: 12px; overflow: hidden; }
        canvas { display: block; background: linear-gradient(to bottom, #4a90e2, #a1c4fd); }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas" width="750" height="420"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // --- HỆ THỐNG ÂM THANH (WEB AUDIO API) ---
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
                osc.frequency.setValueAtTime(50, audioCtx.currentTime);
                osc.frequency.linearRampToValueAtTime(75, audioCtx.currentTime + 0.05);
                gain.gain.setValueAtTime(0.03, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.08);
            } catch(e) {}
        }

        function playEggCrackSound() {
            if (!audioCtx) return;
            try {
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(300, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(80, audioCtx.currentTime + 0.25);
                gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.25);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.25);
            } catch(e) {}
        }

        // --- TRẠNG THÁI GAME ---
        let distance = 0;
        let gameOver = false;
        let keys = {};

        let car = { x: 150, y: 300, vx: 0, ax: 0.18, maxSpeed: 6.5, wheelAngle: 0 };
        let egg = { x: 150, y: 240, angle: 0, angularVel: 0 };

        document.addEventListener("keydown", (e) => {
            initAudio();
            keys[e.key] = true;
            if (gameOver && (e.key === "r" || e.key === "R")) {
                resetGame();
            }
        });
        document.addEventListener("keyup", (e) => keys[e.key] = false);

        function resetGame() {
            distance = 0;
            gameOver = false;
            car.x = 150;
            car.vx = 0;
            car.wheelAngle = 0;
            egg.angle = 0;
            egg.angularVel = 0;
        }

        // Xử lý bấm chuột vào nút Replay / Home trên màn hình thua
        canvas.addEventListener("click", function(event) {
            if (!gameOver) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;

            // Nút Replay
            if (mouseX >= canvas.width / 2 - 110 && mouseX <= canvas.width / 2 + 110 &&
                mouseY >= 235 && mouseY <= 285) {
                resetGame();
            }
            // Nút Home
            else if (mouseX >= canvas.width / 2 - 110 && mouseX <= canvas.width / 2 + 110 &&
                     mouseY >= 300 && mouseY <= 350) {
                resetGame();
            }
        });

        function update() {
            if (gameOver) return;

            let moving = false;
            if (keys["ArrowRight"] || keys["d"] || keys["D"]) {
                car.vx = Math.min(car.vx + car.ax, car.maxSpeed);
                moving = true;
            } else if (keys["ArrowLeft"] || keys["a"] || keys["A"]) {
                car.vx = Math.max(car.vx - car.ax, -car.maxSpeed / 2);
                moving = true;
            } else {
                car.vx *= 0.95; // Ma sát tự nhiên
            }

            if (moving) playEngineSound();

            car.x += car.vx;
            if (car.vx > 0) distance += car.vx * 0.05;
            car.wheelAngle += car.vx * 0.1;

            // Vật lý quán tính của quả trứng
            egg.angularVel += (-car.vx * 0.024);
            egg.angularVel *= 0.91;
            egg.angle += egg.angularVel;
            egg.x = car.x + Math.sin(egg.angle) * 15;

            // Điều kiện trứng vỡ (nghiêng quá góc 1.1 radian ~ 63 độ)
            if (Math.abs(egg.angle) > 1.1) {
                gameOver = true;
                playEggCrackSound();
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Mặt Trời sáng rực phía sau
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(180, 90, 45, 0, Math.PI * 2);
            ctx.fill();

            // 2. Dãy núi phong cách hoạt hình
            ctx.fillStyle = "#5ea63d";
            ctx.beginPath();
            ctx.moveTo(-50, 320);
            ctx.lineTo(120, 180);
            ctx.lineTo(300, 320);
            ctx.lineTo(480, 150);
            ctx.lineTo(700, 320);
            ctx.lineTo(800, 320);
            ctx.lineTo(800, 420);
            ctx.lineTo(-50, 420);
            ctx.fill();

            // 3. Cây cối trang trí
            function drawTree(tx, ty) {
                ctx.fillStyle = "#27ae60";
                ctx.beginPath();
                ctx.arc(tx, ty - 15, 16, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#7f8c8d";
                ctx.fillRect(tx - 25, ty, 6, 15);
            }
            drawTree(120, 290);
            drawTree(380, 260);
            drawTree(580, 280);

            // 4. Mặt đường (Phần trên nhựa đường, phần dưới đất đỏ có hạt hoa văn)
            ctx.fillStyle = "#ecf0f1";
            ctx.fillRect(0, 310, canvas.width, 15);

            ctx.fillStyle = "#c0392b";
            ctx.fillRect(0, 325, canvas.width, 95);

            // Các hạt trên nền đất chuyển động theo xe
            ctx.fillStyle = "#962d22";
            for (let i = 20; i < canvas.width; i += 60) {
                ctx.beginPath();
                ctx.arc(i + ((distance * 2) % 60), 360, 4, 0, Math.PI * 2);
                ctx.arc(i + 30 + ((distance * 2) % 60), 390, 3, 0, Math.PI * 2);
                ctx.fill();
            }

            let screenX = 220; // Vị trí cố định của xe

            // 5. Xe ô tô đỏ đặc trưng (có thanh đỡ trứng và hiển thị mét trên xe)
            ctx.strokeStyle = "#2c3e50";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(screenX - 25, car.y - 5); ctx.lineTo(screenX - 25, car.y - 30);
            ctx.moveTo(screenX + 25, car.y - 5); ctx.lineTo(screenX + 25, car.y - 30);
            ctx.stroke();

            // Thân xe
            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(screenX - 45, car.y - 8, 90, 28);

            // Đèn xe
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(screenX + 42, car.y + 2, 5, 0, Math.PI * 2);
            ctx.fill();

            // Hiển thị mét trên xe
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 14px Arial";
            ctx.fillText(Math.floor(distance) + "m", screenX - 12, car.y + 10);

            // 6. Bánh xe quay
            function drawWheel(wx, wy) {
                ctx.save();
                ctx.translate(wx, wy);
                ctx.rotate(car.wheelAngle);
                ctx.fillStyle = "#2c3e50";
                ctx.beginPath();
                ctx.arc(0, 0, 16, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#ecf0f1";
                ctx.beginPath();
                ctx.arc(0, 0, 7, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            drawWheel(screenX - 28, car.y + 20);
            drawWheel(screenX + 28, car.y + 20);

            // 7. Quả trứng có hiệu ứng phản chiếu ánh sáng (Glossy)
            ctx.save();
            let eggScreenX = screenX + (egg.x - car.x);
            ctx.translate(eggScreenX, car.y - 35);
            ctx.rotate(egg.angle);

            if (!gameOver) {
                ctx.fillStyle = "#fffdf0";
                ctx.beginPath();
                ctx.ellipse(0, 0, 13, 18, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#bdc3c7";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // Điểm sáng bóng loáng trên vỏ trứng
                ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
                ctx.beginPath();
                ctx.ellipse(-4, -6, 3, 5, -0.3, 0, Math.PI * 2);
                ctx.fill();
            } else {
                // Trứng vỡ tóe loe
                ctx.fillStyle = "#f1c40f";
                ctx.beginPath();
                ctx.arc(0, 5, 12, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.arc(-3, -2, 4, 0, Math.PI * 2);
                ctx.arc(5, 3, 3, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();

            // 8. Màn hình Game Over (Giống giao diện game gốc)
            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 28px Arial";
                ctx.textAlign = "center";
                ctx.fillText("Get another chance", canvas.width / 2, 100);

                ctx.fillStyle = "#f1c40f";
                ctx.font = "bold 20px Arial";
                ctx.fillText("Quãng đường: " + Math.floor(distance) + "m", canvas.width / 2, 140);

                // Nút REPLAY
                ctx.fillStyle = "#f39c12";
                ctx.beginPath();
                ctx.roundRect(canvas.width / 2 - 110, 235, 220, 50, 25);
                ctx.fill();
                ctx.strokeStyle = "#fff";
                ctx.lineWidth = 3;
                ctx.stroke();

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 20px Arial";
                ctx.fillText("🔄 REPLAY", canvas.width / 2, 267);

                // Nút HOME
                ctx.fillStyle = "#2ecc71";
                ctx.beginPath();
                ctx.roundRect(canvas.width / 2 - 110, 300, 220, 50, 25);
                ctx.fill();
                ctx.strokeStyle = "#fff";
                ctx.lineWidth = 3;
                ctx.stroke();

                ctx.fillStyle = "#ffffff";
                ctx.fillText("🏠 HOME", canvas.width / 2, 332);
                
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
