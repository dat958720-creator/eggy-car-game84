import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Eggy Car - Phiên Bản Chuẩn", page_icon="🥚", layout="centered"
)

st.title("🥚 Eggy Car - Giống Game Gốc")
st.markdown("""
* **Điều khiển**: Dùng phím **Mũi tên Phải (👉) / D** để tiến, **Mũi tên Trái (👈) / A** để lùi và phanh.
* Giữ cân bằng để quả trứng không bị rơi khỏi xe!
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

        // Trạng thái Game
        let distance = 0;
        let gameOver = false;
        let keys = {};

        let car = { x: 150, y: 300, vx: 0, ax: 0.18, maxSpeed: 6.5, wheelAngle: 0 };
        let egg = { x: 150, y: 245, angle: 0, angularVel: 0 };

        document.addEventListener("keydown", (e) => {
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

        // Xử lý click chuột cho các nút trên màn hình Game Over
        canvas.addEventListener("click", function(event) {
            if (!gameOver) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;

            // Nút Replay (xem vị trí nút vẽ ở dưới)
            if (mouseX >= canvas.width / 2 - 110 && mouseX <= canvas.width / 2 + 110 &&
                mouseY >= 235 && mouseY <= 285) {
                resetGame();
            }
            // Nút Home
            else if (mouseX >= canvas.width / 2 - 110 && mouseX <= canvas.width / 2 + 110 &&
                     Y = mouseY >= 300 && mouseY <= 350) {
                alert("Đã về màn hình chính!");
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
                car.vx *= 0.95; // Ma sát
            }

            car.x += car.vx;
            if (car.vx > 0) distance += car.vx * 0.05;

            car.wheelAngle += car.vx * 0.1;

            // Vật lý quán tính của trứng
            egg.angularVel += (-car.vx * 0.024);
            egg.angularVel *= 0.91;
            egg.angle += egg.angularVel;
            egg.x = car.x + Math.sin(egg.angle) * 15;

            // Kiểm tra trứng rơi / vỡ (nghiêng quá góc 1.1 radian)
            if (Math.abs(egg.angle) > 1.1) {
                gameOver = true;
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ Mặt Trời
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(180, 90, 45, 0, Math.PI * 2);
            ctx.fill();

            // 2. Vẽ Dãy núi phía xa
            ctx.fillStyle = "#6ab04c";
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

            // 3. Vẽ Cây cối nhỏ trang trí giống game gốc
            function drawTree(tx, ty) {
                ctx.fillStyle = "#27ae60";
                ctx.beginPath();
                ctx.arc(tx, ty - 15, 18, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#8e44ad"; // Thân cây / chi tiết
                ctx.fillRect(tx - 3, ty, 6, 15);
            }
            drawTree(120, 290);
            drawTree(380, 260);
            drawTree(580, 280);

            // 4. Vẽ Mặt đường (Phần trên màu xám trắng, phần dưới là đất đỏ nâu có hạt)
            // Đường nhựa
            ctx.fillStyle = "#ecf0f1";
            ctx.fillRect(0, 310, canvas.width, 15);

            // Phần đất đỏ bên dưới
            ctx.fillStyle = "#c0392b";
            ctx.fillRect(0, 325, canvas.width, 95);

            // Các hạt chấm trên nền đất
            ctx.fillStyle = "#962d22";
            for (let i = 20; i < canvas.width; i += 60) {
                ctx.beginPath();
                ctx.arc(i + ((distance * 2) % 60), 360, 4, 0, Math.PI * 2);
                ctx.arc(i + 30 + ((distance * 2) % 60), 390, 3, 0, Math.PI * 2);
                ctx.fill();
            }

            let screenX = 220; // Vị trí xe trên màn hình

            // 5. Vẽ Xe Ô tô màu đỏ đặc trưng
            // Thanh đỡ trứng phía sau
            ctx.strokeStyle = "#2c3e50";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(screenX - 25, car.y - 5); ctx.lineTo(screenX - 25, car.y - 30);
            ctx.moveTo(screenX + 25, car.y - 5); ctx.lineTo(screenX + 25, car.y - 30);
            ctx.stroke();

            // Thân xe chính
            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(screenX - 45, car.y - 8, 90, 28);

            // Đèn xe
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(screenX + 42, car.y + 2, 5, 0, Math.PI * 2);
            ctx.fill();

            // Hiển thị số mét trên thân xe giống mẫu[cite: 1]
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 14px Arial";
            ctx.fillText(Math.floor(distance) + "m", screenX - 12, car.y + 10);

            // 6. Vẽ Bánh xe có viền trắng đứt đoạn
            function drawWheel(wx, wy) {
                ctx.save();
                ctx.translate(wx, wy);
                ctx.rotate(car.wheelAngle);
                ctx.fillStyle = "#2c3e50";
                ctx.beginPath();
                ctx.arc(0, 0, 16, 0, Math.PI * 2);
                ctx.fill();
                // Vâm bánh xe trắng
                ctx.fillStyle = "#ecf0f1";
                ctx.beginPath();
                ctx.arc(0, 0, 7, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            drawWheel(screenX - 28, car.y + 20);
            drawWheel(screenX + 28, car.y + 20);

            // 7. Vẽ Quả Trứng bên trên xe
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
            } else {
                // Trứng vỡ tóe loe khi thua
                ctx.fillStyle = "#f1c40f";
                ctx.beginPath();
                ctx.arc(0, 5, 12, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();

            // 8. Giao diện Game Over (Giống màn hình "Get another chance" trong ảnh mẫu)[cite: 1]
            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Tiêu đề
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 28px Arial";
                ctx.textAlign = "center";
                ctx.fillText("Get another chance", canvas.width / 2, 100);

                // Hiển thị điểm số đạt được
                ctx.fillStyle = "#f1c40f";
                ctx.font = "bold 20px Arial";
                ctx.fillText("Quãng đường: " + Math.floor(distance) + "m", canvas.width / 2, 140);

                // Nút REPLAY (Màu vàng cam)[cite: 1]
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

                // Nút HOME (Màu xanh lá)[cite: 1]
                ctx.fillStyle = "#2ecc71";
                ctx.beginPath();
                ctx.roundRect(canvas.width / 2 - 110, 300, 220, 50, 25);
                ctx.fill();
                ctx.strokeStyle = "#fff";
                ctx.lineWidth = 3;
                ctx.stroke();

                ctx.fillStyle = "#ffffff";
                ctx.fillText("🏠 HOME", canvas.width / 2, 332);
                
                ctx.textAlign = "left"; // Reset alignment
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
