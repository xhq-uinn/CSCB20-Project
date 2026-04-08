const btn = document.getElementById("welcome");
btn.addEventListener("click", function () {
    window.location.href = "/";
});


const sellbtn = document.getElementById("sell");
sellbtn.addEventListener("click", function () {
    window.location.href = "/sell";
});

const logInBtn = document.getElementByID("login");
logInBtn.addEventListener("click", function(){
    window.location.href = "/login"
});

const signUpBtn = document.getElementByID("signup")
signUpBtn.addEventListener("click", function(){
    window.location.href = "/signup"
});