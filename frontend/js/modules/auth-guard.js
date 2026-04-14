import { clearStoredToken, getStoredToken } from "../api.js";

export function requireAuth(redirectUrl = "./auth.html") {
  const token = getStoredToken();
  if (token) {
    return token;
  }

  window.location.href = redirectUrl;
  return null;
}

export function handleUnauthorized(redirectUrl = "./auth.html") {
  clearStoredToken();
  window.location.href = `${redirectUrl}?reason=expired`;
}
