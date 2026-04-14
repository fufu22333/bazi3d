import {
  deleteWorkDetail,
  fetchWorkDetail,
  getStoredUser,
  updateWorkDetail,
} from "./api.js";
import { createViewerRuntime } from "./viewer/runtime.js";

const titleNode = document.getElementById("work-title");
const descriptionNode = document.getElementById("work-description");
const authorNode = document.getElementById("work-author");
const visibilityNode = document.getElementById("work-visibility");
const createdAtNode = document.getElementById("work-created-at");
const tagsNode = document.getElementById("work-tags");
const statusNode = document.getElementById("work-status");
const managePanelNode = document.getElementById("work-manage-panel");
const manageStatusNode = document.getElementById("work-manage-status");
const editForm = document.getElementById("edit-work-form");
const editTitleInput = document.getElementById("edit-title");
const editDescriptionInput = document.getElementById("edit-description");
const editVisibilityInput = document.getElementById("edit-visibility");
const editAllowRemixInput = document.getElementById("edit-allow-remix");

let currentWork = null;

const viewerRuntime = createViewerRuntime({
  canvas: document.getElementById("viewer-canvas"),
  statusNode: document.getElementById("work-viewer-status"),
  motionStatusNode: document.getElementById("work-motion-status"),
  interactionStatusNode: document.getElementById("work-interaction-status"),
  personUrlInput: document.getElementById("person-url"),
  guardianUrlInput: document.getElementById("guardian-url"),
  resourceTypeSelect: document.getElementById("resource-type"),
  skyboxUrlInput: document.getElementById("skybox-url"),
});

function formatVisibility(value) {
  if (value === "public") {
    return "公开";
  }
  if (value === "private") {
    return "私密";
  }
  return "未知";
}

function formatResourceLabel(value) {
  return value === "guardian" ? "守护灵" : "人物";
}

function getWorkIdFromLocation() {
  const params = new URLSearchParams(window.location.search);
  const paramId = params.get("id");
  if (paramId) {
    return paramId;
  }

  const segments = window.location.pathname.split("/").filter(Boolean);
  const lastSegment = segments[segments.length - 1];
  if (lastSegment && /^\d+$/.test(lastSegment)) {
    return lastSegment;
  }

  return "";
}

function renderTags(tags) {
  tagsNode.innerHTML = "";
  if (!Array.isArray(tags) || tags.length === 0) {
    const emptyNode = document.createElement("span");
    emptyNode.className = "tag";
    emptyNode.textContent = "暂无风格标签";
    tagsNode.append(emptyNode);
    return;
  }

  tags.forEach((tag) => {
    const tagNode = document.createElement("span");
    tagNode.className = "tag";
    tagNode.textContent = tag;
    tagsNode.append(tagNode);
  });
}

function toggleManagePanel(work) {
  const storedUser = getStoredUser();
  const isOwner = Boolean(storedUser?.id && storedUser.id === work.author?.id);

  managePanelNode.classList.toggle("is-hidden", !isOwner);
  if (!isOwner) {
    manageStatusNode.textContent = "作者控制区已隐藏。";
    return;
  }

  manageStatusNode.textContent = "你是这件作品的作者，修改将直接保存到当前作品。";
  editTitleInput.value = work.title || "";
  editDescriptionInput.value = work.description || "";
  editVisibilityInput.value = work.visibility || "public";
  editAllowRemixInput.checked = Boolean(work.allow_remix);
}

function renderWorkDetail(work) {
  currentWork = work;
  titleNode.textContent = work.title;
  descriptionNode.textContent = work.description || "暂无描述。";
  authorNode.textContent = work.author?.username || "未知";
  visibilityNode.textContent = formatVisibility(work.visibility);
  createdAtNode.textContent = work.created_at || "未知";
  statusNode.textContent = "作品详情已加载。";
  renderTags(work.style_tags || []);
  toggleManagePanel(work);

  if (work.asset?.url) {
    document.getElementById("person-url").value = work.asset.url;
    viewerRuntime.setStatus("只读作品资源已就绪，可直接加载。");
    void viewerRuntime.loadSelectedModel();
  } else {
    viewerRuntime.setStatus("这件作品没有可加载的资源地址。");
  }
}

async function handleSaveSubmit(event) {
  event.preventDefault();
  if (!currentWork) {
    return;
  }

  manageStatusNode.textContent = "正在保存作品修改...";

  try {
    const updatedWork = await updateWorkDetail(currentWork.id, {
      title: editTitleInput.value.trim(),
      description: editDescriptionInput.value,
      visibility: editVisibilityInput.value,
      allow_remix: editAllowRemixInput.checked,
    });
    manageStatusNode.textContent = "作品已更新。";
    renderWorkDetail(updatedWork);
  } catch (error) {
    manageStatusNode.textContent = error.message || "更新作品失败。";
  }
}

async function handleDeleteClick() {
  if (!currentWork) {
    return;
  }

  manageStatusNode.textContent = "正在删除作品...";

  try {
    await deleteWorkDetail(currentWork.id);
    window.location.href = "./gallery.html";
  } catch (error) {
    manageStatusNode.textContent = error.message || "删除作品失败。";
  }
}

export async function loadWorkDetail() {
  const workId = getWorkIdFromLocation();
  if (!workId) {
    statusNode.textContent = "缺少作品 ID。";
    titleNode.textContent = "未找到作品";
    return;
  }

  statusNode.textContent = `正在加载作品 #${workId}...`;

  try {
    const work = await fetchWorkDetail(workId);
    renderWorkDetail(work);
  } catch (error) {
    statusNode.textContent = error.message || "加载作品详情失败。";
    titleNode.textContent = "未找到作品";
    viewerRuntime.setStatusError("无法加载该作品的资源。");
  }
}

document.getElementById("load-model").addEventListener("click", () => {
  void viewerRuntime.loadSelectedModel();
});

document.getElementById("play-idle").addEventListener("click", () => {
  viewerRuntime.playClip("idle");
});

document.getElementById("play-wave").addEventListener("click", () => {
  viewerRuntime.playClip("wave");
});

document.getElementById("resource-type").addEventListener("change", () => {
  viewerRuntime.setStatus(
    `已选择${formatResourceLabel(document.getElementById("resource-type").value)}模型。`
  );
});

editForm.addEventListener("submit", (event) => {
  void handleSaveSubmit(event);
});

document.getElementById("delete-work").addEventListener("click", () => {
  void handleDeleteClick();
});

void loadWorkDetail();
