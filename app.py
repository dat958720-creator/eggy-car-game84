import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Eggy Car Mini", page_icon="🥚", layout="centered"
)

st.title("🥚 Eggy Car - Game Lái Xe Chở Trứng")
st.write(
    "Dùng bàn phím **Phím Mũi Tên Phải (👉) / D** để tiến, **Phím Mũi Tên Trái (👈) / A** để lùi và phanh. Giữ cân bằng không làm vỡ trứng!"
)

# Mã HTML/CSS/JavaScript xử lý game vật lý 2D
eggy_car_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #222; text-align: center; color: white; font-family: sans-serif; }
        canvas { background: linear-gradient(to bottom, #87CEEB, #E0F6FF); display: block; margin: 10px auto; border-radius: 8px; }
        #info { font-size: 18px; font-weight: bold; margin-top: 5px; }
    </style>
</head>
<body>
    <div id="info">Khoảng cách: <span id="score">0</span>m</div>
    <canvas id="gameCanvas" width="700" height="400"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Trạng thái Game
        let distance = 0;
        let gameOver = false;
        let keys = {};

        // Đối tượng Xe & Trứng
        let car = { x: 100, y: 300, vx: 0, ax: 0.15, maxSpeed: 6 };
        let egg = { x: 100, y: 265, vx: 0, angle: 0, angularVel: 0 };

        document.addEventListener("keydown", (e) => keys[e.key] = true);
        document.addEventListener("keyup", (e) => keys[e.key] = false);

        function update() {
            if (gameOver) return;

            // Xử lý di chuyển xe
            if (keys["ArrowRight"] || keys["d"] || keys["D"]) {
                car.vx = Math.min(car.vx + car.ax, car.maxSpeed);
            } else if (keys["ArrowLeft"] || keys["a"] || keys["A"]) {
                car.vx = Math.max(car.vx - car.ax, -car.maxSpeed / 2);
            } else {
                car.vx *= 0.96; // Lực ma sát tự nhiên
            }

            car.x += car.vx;
            if (car.vx > 0) distance += car.vx * 0.05;

            // Quả trứng chịu tác động gia tốc của xe (Quán tính)
            egg.angularVel += (-car.vx * 0.02); // Gia tốc xe khiến trứng nghiêng
            egg.angularVel *= 0.92; // Lực cản không khí
            egg.angle += egg.angularVel;
            egg.x = car.x + Math.sin(egg.angle) * 15;

            // Kiểm tra điều kiện ngã/vỡ trứng (nghiêng quá 70 độ)
            if (Math.abs(egg.angle) > 1.2) {
                gameOver = true;
            }

            document.getElementById("score").innerText = Math.floor(distance);
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ Mặt đường đồi núi đơn giản
            ctx.fillStyle = "#4CAF50";
            ctx.beginPath();
            ctx.arc(350, 650, 400, 0, Math.PI * 2);
            ctx.fill();

            // Tọa độ hiển thị tương đối trên Canvas
            let screenX = 200; 

            // Vẽ Bánh xe
            ctx.fillStyle = "#333";
            ctx.beginPath();
            ctx.arc(screenX - 25, car.y + 20, 15, 0, Math.PI * 2);
            ctx.arc(screenX + 25, car.y + 20, 15, 0, Math.PI * 2);
            ctx.fill();

            // Vẽ Thân xe
            ctx.fillStyle = "#FF5722";
            ctx.fillRect(screenX - 40, car.y - 10, 80, 30);

            // Vẽ Quả trứng
            ctx.save();
            ctx.translate(screenX + (egg.x - car.x), car.y - 25);
            ctx.rotate(egg.angle);
            
            ctx.fillStyle = gameOver ? "#FF0000" : "#FFF8DC";
            ctx.beginPath();
            ctx.ellipse(0, 0, 14, 20, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = "#D2B48C";
            ctx.lineWidth = 2;
            ctx.stroke();
            
            ctx.restore();

            if (gameOver) {
                ctx.fillStyle = "rgba(0,0,0,0.7)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#FF4D4D";
                ctx.font = "30px Arial";
                ctx.fillText("💥 TRỨNG ĐÃ VỠ!", canvas.width / 2 - 120, canvas.height / 2 - 10);
                ctx.fillStyle = "#FFF";
                ctx.font = "18px Arial";
                ctx.fillText("Nhấn F5 (hoặc Load lại) để chơi lại", canvas.width / 2 - 140, canvas.height / 2 + 30);
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

# Nhúng mã game HTML vào Streamlit
components.html(eggy_car_html, height=500)
