import { fetchMyWorks, getStoredUser } from "./api.js";
import { requireAuth } from "./modules/auth-guard.js";

const usernameNode = document.getElementById("profile-username");
const emailNode = document.getElementById("profile-email");
const statusNode = document.getElementById("profile-status");
const worksListNode = document.getElementById("profile-works-list");

function buildWorkDetailUrl(work) {
  return `./work.html?id=${work.id}`;
}

function renderUserSummary() {
  const storedUser = getStoredUser();
  usernameNode.textContent = storedUser?.username || "已登录用户";
  emailNode.textContent = storedUser?.email || "本地会话中没有可用邮箱。";
}

function formatVisibility(value) {
  if (value === "public") {
    return "公开";
  }
  if (value === "private") {
    return "私密";
  }
  return "未知";
}

function renderWorks(items) {
  worksListNode.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    const emptyNode = document.createElement("div");
    emptyNode.className = "work-card";
    emptyNode.textContent = "你还没有发布任何作品。";
    worksListNode.append(emptyNode);
    return;
  }

  items.forEach((work) => {
    const card = document.createElement("article");
    card.className = "work-card";

    const title = document.createElement("h3");
    title.textContent = work.title || "未命名作品";

    const description = document.createElement("p");
    description.className = "muted";
    description.textContent = work.description || "暂无描述。";

    const meta = document.createElement("p");
    meta.className = "muted";
    meta.textContent = `可见性：${formatVisibility(work.visibility)}`;

    const link = document.createElement("a");
    link.href = buildWorkDetailUrl(work);
    link.textContent = "打开作品详情";

    card.append(title, description, meta, link);
    worksListNode.append(card);
  });
}

export async function loadProfilePage() {
  const token = requireAuth();
  if (!token) {
    return;
  }

  renderUserSummary();
  statusNode.textContent = "正在加载你的作品...";

  try {
    const payload = await fetchMyWorks();
    renderWorks(payload.items);
    statusNode.textContent = `已加载 ${payload.items.length} 个作品。`;
  } catch (error) {
    statusNode.textContent = error.message || "加载你的作品失败。";
  }
}

void loadProfilePage();
