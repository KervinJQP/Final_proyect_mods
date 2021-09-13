const loginForm = document.getElementById("login-form");
const loginButton = document.getElementById("login-form-submit");
// const loginErrorMsg = document.getElementById("login-error-msg");
// const loginErrorMsgform = document.getElementById("login-error-msg-form");


loginButton.addEventListener("click", (e) => {
    e.preventDefault();
    const username = loginForm.username.value;
    const password = loginForm.password.value;
    //windoes.alert(username,password);
    if (username === "kervinjosueq" && password === "11998690") {
        //alert("You have successfully logged in.");
        location.href = "/home" ;

        //location.reload();
    } else {
        alert("Incorrect credentials");
        // loginErrorMsg.style.opacity = 1;
        // loginErrorMsgform.style.opacity = 1;
    }
})