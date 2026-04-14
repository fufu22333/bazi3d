const TOKEN_STORAGE_KEY = "bazi3d.token";
const USER_STORAGE_KEY = "bazi3d.user";

function getStoredToken() {
  return window.localStorage.getItem("bazi3d.token") || "";
}

function clearStoredSession() {
  window.localStorage.removeItem("bazi3d.token");
  window.localStorage.removeItem("bazi3d.user");
}

function resolveCurrentPage(root) {
  const explicitPage = root.dataset.navPage;
  if (explicitPage) {
    return explicitPage;
  }

  const pathname = window.location.pathname;
  if (pathname.endsWith("/app") || pathname.endsWith("/index.html")) {
    return "home";
  }
  if (pathname.endsWith("/gallery.html")) {
    return "gallery";
  }
  if (pathname.endsWith("/profile.html")) {
    return "profile";
  }
  return "";
}

function updateCurrentPageState(root) {
  const currentPage = resolveCurrentPage(root);
  const links = root.querySelectorAll("[data-nav-link]");

  links.forEach((link) => {
    const isCurrent = link.dataset.navLink === currentPage;
    link.classList.toggle("is-current", isCurrent);
    if (isCurrent) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
}

function bindAuthButton(root) {
  const button = root.querySelector("[data-nav-auth]");
  if (!button) {
    return;
  }

  const isLoggedIn = Boolean(getStoredToken());
  if (isLoggedIn) {
    button.textContent = "退出登录";
    button.dataset.mode = "logout";
  } else {
    button.textContent = "登录";
    button.dataset.mode = "login";
  }

  button.addEventListener("click", () => {
    if (button.dataset.mode === "logout") {
      clearStoredSession();
    }
    window.location.href = "./auth.html";
  });
}

function initializeNav(root) {
  updateCurrentPageState(root);
  bindAuthButton(root);
}

document.querySelectorAll("[data-nav-root]").forEach((root) => {
  initializeNav(root);
});
