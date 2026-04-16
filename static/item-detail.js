
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

function scalePage() {
    const wrapper = document.querySelector(".scale-wrapper");
    if (!wrapper) return;

    const baseWidth = 1200;
    const currentWidth = window.innerWidth;

    const scale = currentWidth / baseWidth;

    wrapper.style.transform = `scale(${scale})`;
}

window.addEventListener("resize", scalePage);
window.addEventListener("load", scalePage);