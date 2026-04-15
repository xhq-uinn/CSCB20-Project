
const modal = document.getElementById("modalOverlay");
const buyBtn = document.getElementById("buyBtn");
const closeBtn = document.getElementById("closeBtn");

// 点击 Buy → 显示
buyBtn.onclick = function() {
    modal.style.display = "flex";
}

// 点击 X → 关闭
closeBtn.onclick = function() {
    modal.style.display = "none";
}

// 点击背景 → 关闭
modal.onclick = function(e) {
    if (e.target === modal) {
        modal.style.display = "none";
    }
}