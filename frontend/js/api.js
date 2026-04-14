const API_BASE_URL = "";
const TOKEN_STORAGE_KEY = "bazi3d.token";
const USER_STORAGE_KEY = "bazi3d.user";

export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY) || "";
}

export function setStoredToken(token) {
  if (!token) {
    clearStoredToken();
    return;
  }
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredToken() {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  window.localStorage.removeItem(USER_STORAGE_KEY);
}

export function getStoredUser() {
  const rawUser = window.localStorage.getItem(USER_STORAGE_KEY);
  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch (error) {
    window.localStorage.removeItem(USER_STORAGE_KEY);
    return null;
  }
}

export function setStoredSession(payload) {
  if (!payload?.token) {
    return;
  }

  setStoredToken(payload.token);
  if (payload.user) {
    window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(payload.user));
  }
}

function buildHeaders(token = getStoredToken()) {
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);

  if (response.status === 401) {
    clearStoredToken();
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      payload?.error?.message ||
      payload?.error ||
      `请求失败：${response.status}`;
    throw new Error(message);
  }

  return payload;
}

export async function loginUser(payload) {
  return requestJson("/api/auth/login", {
    method: "POST",
    headers: buildHeaders(""),
    body: JSON.stringify(payload),
  });
}

export async function registerUser(payload) {
  return requestJson("/api/auth/register", {
    method: "POST",
    headers: buildHeaders(""),
    body: JSON.stringify(payload),
  });
}

export async function createTask(token, payload) {
  return requestJson("/api/tasks", {
    method: "POST",
    headers: buildHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function fetchTask(token, taskId) {
  return requestJson(`/api/tasks/${taskId}`, {
    method: "GET",
    headers: buildHeaders(token),
  });
}

export async function fetchWorks() {
  return requestJson("/api/works", {
    method: "GET",
    headers: buildHeaders(),
  });
}

export async function fetchMyWorks() {
  return requestJson("/api/works/mine", {
    method: "GET",
    headers: buildHeaders(),
  });
}

export async function fetchWorkDetail(workId) {
  return requestJson(`/api/works/${workId}`, {
    method: "GET",
    headers: buildHeaders(),
  });
}

export async function updateWorkDetail(workId, payload) {
  return requestJson(`/api/works/${workId}`, {
    method: "PATCH",
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  });
}

export async function deleteWorkDetail(workId) {
  const response = await fetch(`${API_BASE_URL}/api/works/${workId}`, {
    method: "DELETE",
    headers: buildHeaders(),
  });

  if (response.status === 401) {
    clearStoredToken();
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message =
      payload?.error?.message ||
      payload?.error ||
      `请求失败：${response.status}`;
    throw new Error(message);
  }
}

export async function sendCharacterChat(token, payload) {
  return requestJson("/api/chat", {
    method: "POST",
    headers: buildHeaders(token),
    body: JSON.stringify(payload),
  });
}
