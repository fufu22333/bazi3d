import { fetchMyWorks, getStoredUser } from "./api.js";
import { requireAuth } from "./modules/auth-guard.js";

const usernameNode = document.getElementById("profile-username");
const emailNode = document.getElementById("profile-email");
const statusNode = document.getElementById("profile-status");
const worksListNode = document.getElementById("profile-works-list");
const workCountNode = document.getElementById("profile-work-count");
const publicCountNode = document.getElementById("profile-public-count");
const assetCountNode = document.getElementById("profile-asset-count");

function buildWorkDetailUrl(work) {
  return `./work.html?id=${work.id}`;
}

function getViewerResourceType(work) {
  return work.asset?.type === "guardian" ? "guardian" : "person";
}

function buildViewerUrl(work) {
  const resourceType = getViewerResourceType(work);
  const params = new URLSearchParams({
    resourceType,
    autoload: "1",
  });
  params.set(resourceType === "guardian" ? "guardianUrl" : "personUrl", work.asset?.url || "");
  return `./viewer.html?${params.toString()}`;
}

function renderUserSummary() {
  const storedUser = getStoredUser();
  usernameNode.textContent = storedUser?.username || "已登录用户";
  emailNode.textContent = storedUser?.email || "当前会话暂无邮箱信息";
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

function formatAssetType(work) {
  const url = work.asset?.url || "";
  if (url.includes("guardian")) {
    return "守护灵模型";
  }
  if (url.includes("character")) {
    return "人物模型";
  }
  return "GLB 模型";
}

function createWorkRow(work) {
  const row = document.createElement("article");
  row.className = "work-row";

  const titleBlock = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = work.title || "未命名作品";
  const description = document.createElement("p");
  description.className = "muted";
  description.textContent = work.description || "暂无作品描述。";
  titleBlock.append(title, description);

  const assetBlock = document.createElement("div");
  assetBlock.className = "asset-line";
  const assetType = document.createElement("span");
  assetType.className = "asset-type";
  assetType.textContent = formatAssetType(work);
  const visibility = document.createElement("span");
  visibility.textContent = `可见性：${formatVisibility(work.visibility)}`;
  assetBlock.append(assetType, visibility);

  const actions = document.createElement("div");
  actions.className = "work-actions";
  const detailLink = document.createElement("a");
  detailLink.href = buildWorkDetailUrl(work);
  detailLink.textContent = "查看详情";
  actions.append(detailLink);

  if (work.asset?.url && work.asset?.is_available !== false) {
    const viewerLink = document.createElement("a");
    viewerLink.href = buildViewerUrl(work);
    viewerLink.textContent = "打开查看器";
    actions.append(viewerLink);

    const downloadLink = document.createElement("a");
    downloadLink.href = work.asset.url;
    downloadLink.download = `${work.title || "bazi3d-model"}.glb`;
    downloadLink.textContent = "下载模型";
    actions.append(downloadLink);
  }

  row.append(titleBlock, assetBlock, actions);
  return row;
}

function renderWorks(items) {
  worksListNode.innerHTML = "";
  const safeItems = Array.isArray(items) ? items : [];
  const publicItems = safeItems.filter((work) => work.visibility === "public");
  const assetItems = safeItems.filter(
    (work) => Boolean(work.asset?.url) && work.asset?.is_available !== false,
  );

  workCountNode.textContent = String(safeItems.length);
  publicCountNode.textContent = String(publicItems.length);
  assetCountNode.textContent = String(assetItems.length);

  if (safeItems.length === 0) {
    const emptyNode = document.createElement("div");
    emptyNode.className = "work-row";
    emptyNode.textContent = "当前账号还没有作品。";
    worksListNode.append(emptyNode);
    return;
  }

  safeItems.forEach((work) => {
    worksListNode.append(createWorkRow(work));
  });
}

export async function loadProfilePage() {
  const token = requireAuth();
  if (!token) {
    return;
  }

  renderUserSummary();
  statusNode.textContent = "正在加载作品管理数据...";

  try {
    const payload = await fetchMyWorks();
    renderWorks(payload.items);
    statusNode.textContent = `已加载 ${payload.items.length} 个作品。`;
  } catch (error) {
    statusNode.textContent = error.message || "加载作品管理数据失败。";
  }
}

void loadProfilePage();
