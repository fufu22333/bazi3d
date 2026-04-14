import {
  getStoredToken,
  loginUser,
  registerUser,
  setStoredSession,
} from "./api.js";

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const statusNode = document.getElementById("auth-status");

function setStatus(message, isError = false) {
  statusNode.textContent = message;
  statusNode.style.color = isError ? "#b91c1c" : "#065f46";
}

function redirectToCreate() {
  window.location.href = "./index.html";
}

async function handleLoginSubmit(event) {
  event.preventDefault();

  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value.trim();

  setStatus("正在登录...");

  try {
    const payload = await loginUser({ email, password });
    setStoredSession(payload);
    setStatus("登录成功，正在跳转...");
    redirectToCreate();
  } catch (error) {
    setStatus(error.message || "登录失败。", true);
  }
}

async function handleRegisterSubmit(event) {
  event.preventDefault();

  const email = document.getElementById("register-email").value.trim();
  const username = document.getElementById("register-username").value.trim();
  const password = document.getElementById("register-password").value.trim();

  setStatus("正在创建账号...");

  try {
    const payload = await registerUser({ email, username, password });
    setStoredSession(payload);
    setStatus("注册成功，正在跳转...");
    redirectToCreate();
  } catch (error) {
    setStatus(error.message || "注册失败。", true);
  }
}

if (getStoredToken()) {
  setStatus("你已经登录，正在跳转...");
  redirectToCreate();
}

loginForm.addEventListener("submit", (event) => {
  void handleLoginSubmit(event);
});

registerForm.addEventListener("submit", (event) => {
  void handleRegisterSubmit(event);
});
