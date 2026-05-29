import * as THREE from "https://esm.sh/three@0.165.0";
import { OrbitControls } from "https://esm.sh/three@0.165.0/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "https://esm.sh/three@0.165.0/examples/jsm/loaders/GLTFLoader.js";
import {
  createTask,
  fetchTask,
  getStoredToken,
  sendCharacterChat,
} from "../api.js";
import { handleUnauthorized, requireAuth } from "../modules/auth-guard.js";
import { applySkyboxBackground } from "./skybox.js";
import { createAnimationLayer } from "./animation.js";
import { attachModelInteraction } from "./interaction.js";

const canvas = document.getElementById("viewer-canvas");
const taskForm = document.getElementById("task-form");
const displayNameInput = document.getElementById("display-name");
const genderInput = document.getElementById("gender");
const birthLocationInput = document.getElementById("birth-location");
const birthDateTimeInput = document.getElementById("birth-datetime");
const referenceImageUrlInput = document.getElementById("reference-image-url");
const extraNoteInput = document.getElementById("extra-note");
const fashionStyleInput = document.getElementById("fashion-style");
const spiritStyleInput = document.getElementById("spirit-style");
const resetTaskFormButton = document.getElementById("reset-task-form");
const taskStatusNode = document.getElementById("task-status");
const taskMetaNode = document.getElementById("task-meta");
const taskHintNode = document.getElementById("task-hint");
const taskDetailLink = document.getElementById("task-detail-link");
const skyboxUrlInput = document.getElementById("skybox-url");
const motionStatusNode = document.getElementById("motion-status");
const playIdleButton = document.getElementById("play-idle");
const playWaveButton = document.getElementById("play-wave");
const triggerGreetButton = document.getElementById("trigger-greet");
const interactionStatusNode = document.getElementById("interaction-status");
const personFileInput = document.getElementById("person-file");
const guardianFileInput = document.getElementById("guardian-file");
const personUrlInput = document.getElementById("person-url");
const guardianUrlInput = document.getElementById("guardian-url");
const resourceTypeSelect = document.getElementById("resource-type");
const loadButton = document.getElementById("load-model");
const statusNode = document.getElementById("viewer-status");
const resultPlaceholderNode = document.getElementById("result-placeholder");
const chatLogNode = document.getElementById("chat-log");
const chatInput = document.getElementById("chat-input");
const sendChatButton = document.getElementById("send-chat");
const NO_MODEL_INTERACTION_STATUS = "悬停交互：请先加载模型。";

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf3f3f3);

const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
camera.position.set(0, 1.5, 4);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.target.set(0, 1, 0);

const hemiLight = new THREE.HemisphereLight(0xffffff, 0x888888, 1.5);
scene.add(hemiLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
dirLight.position.set(4, 6, 3);
scene.add(dirLight);

const grid = new THREE.GridHelper(10, 10);
scene.add(grid);

const loader = new GLTFLoader();
const textureLoader = new THREE.TextureLoader();
const clock = new THREE.Clock();
let currentModel = null;
let pollTimer = null;
const initialParams = new URLSearchParams(window.location.search);
const animationLayer = createAnimationLayer({
  motionStatusNode,
  interactionStatusNode,
});
const recentChatMessages = [];
const authToken = requireAuth();
const localModelSources = {
  person: { objectUrl: "", fileName: "" },
  guardian: { objectUrl: "", fileName: "" },
};

function formatTaskStatus(status) {
  const labels = {
    idle: "空闲中",
    submitting: "提交中",
    pending: "处理中",
    completed: "已完成",
    failed: "失败",
  };
  return labels[status] || status || "空闲中";
}

function formatResourceLabel(value) {
  return value === "guardian" ? "守护灵" : "人物";
}

function setStatus(message) {
  statusNode.textContent = message;
}

function getResourceInputs(resourceType) {
  return resourceType === "guardian"
    ? {
        fileInput: guardianFileInput,
        urlInput: guardianUrlInput,
        localSource: localModelSources.guardian,
      }
    : {
        fileInput: personFileInput,
        urlInput: personUrlInput,
        localSource: localModelSources.person,
      };
}

function clearLocalObjectUrl(localSource) {
  if (!localSource.objectUrl) {
    return;
  }
  URL.revokeObjectURL(localSource.objectUrl);
  localSource.objectUrl = "";
  localSource.fileName = "";
}

function clearResourceFileSelection(resourceType) {
  const { fileInput, localSource } = getResourceInputs(resourceType);
  clearLocalObjectUrl(localSource);
  fileInput.value = "";
}

function setTaskStatus(message) {
  taskStatusNode.textContent = message;
  taskStatusNode.classList.remove("is-error");
}

function setTaskStatusError(message) {
  taskStatusNode.textContent = message;
  taskStatusNode.classList.add("is-error");
}

function setResultPlaceholder(message) {
  resultPlaceholderNode.textContent = message;
  resultPlaceholderNode.classList.remove("is-hidden");
}

function hideResultPlaceholder() {
  resultPlaceholderNode.classList.add("is-hidden");
}

function getChatSpeakerLabel(role) {
  if (role === "user") {
    return "你";
  }
  if (role === "system") {
    return "系统";
  }
  return displayNameInput.value.trim() || "角色";
}

function scrollChatLogToBottom() {
  chatLogNode.scrollTop = chatLogNode.scrollHeight;
}

function createChatMessageNode(role, content, { isError = false } = {}) {
  const messageNode = document.createElement("div");
  const variantClass =
    role === "user"
      ? "chat-message--user"
      : role === "system"
        ? "chat-message--system"
        : "chat-message--character";

  messageNode.className = `chat-message ${variantClass}`;
  if (isError) {
    messageNode.classList.add("is-error");
  }

  const nameNode = document.createElement("div");
  nameNode.className = "chat-message__name";
  nameNode.textContent = getChatSpeakerLabel(role);

  const contentNode = document.createElement("div");
  contentNode.className = "chat-message__content";
  contentNode.textContent = content;

  messageNode.append(nameNode, contentNode);
  return messageNode;
}

function renderChatMessages() {
  chatLogNode.replaceChildren();

  if (recentChatMessages.length === 0) {
    chatLogNode.append(
      createChatMessageNode("system", "角色对话：空闲中。"),
    );
    scrollChatLogToBottom();
    return;
  }

  recentChatMessages.forEach((item) => {
    chatLogNode.append(createChatMessageNode(item.role, item.content));
  });
  scrollChatLogToBottom();
}

function setChatLogStatus(message, { isError = false } = {}) {
  chatLogNode.replaceChildren(
    createChatMessageNode("system", message, { isError }),
  );
  scrollChatLogToBottom();
}

function renderTaskState({ status, taskId = null, hasAssets = false, note = "" }) {
  const normalizedStatus = status || "idle";
  setTaskStatus(`任务${formatTaskStatus(normalizedStatus)}。`);
  taskMetaNode.textContent = taskId
    ? `任务 #${taskId}${hasAssets ? " 已返回查看器资源。" : " 仍在等待查看器资源。"}`
    : "尚未提交任务。";
  if (taskId) {
    taskDetailLink.href = `./task.html?taskId=${encodeURIComponent(taskId)}`;
    taskDetailLink.classList.remove("is-hidden");
  } else {
    taskDetailLink.classList.add("is-hidden");
  }

  if (note) {
    taskHintNode.textContent = note;
  } else if (normalizedStatus === "pending") {
    taskHintNode.textContent =
      "任务正在处理中。当前后端链路可能会持续等待一段时间，所以结果区域可能继续显示占位提示。";
  } else if (normalizedStatus === "completed" && !hasAssets) {
    taskHintNode.textContent =
      "任务已完成，但还没有返回资源。在后端提供结果地址之前，占位提示会继续显示。";
  } else if (normalizedStatus === "completed" && hasAssets) {
    taskHintNode.textContent =
      "资源已就绪。可以使用查看器控件检查人物和守护灵模型。";
  } else if (normalizedStatus === "failed") {
    taskHintNode.textContent =
      "任务失败。你可以直接调整输入并重新提交，无需离开当前页面。";
  } else {
    taskHintNode.textContent =
      "提交表单后即可创建任务。如果资源暂未返回，结果区域会继续显示占位提示。";
  }

  if (hasAssets) {
    hideResultPlaceholder();
    return;
  }

  setResultPlaceholder("尚未生成资源。提交任务后可填充查看器，也可以先停留在这里观察处理中状态。");
}

function appendChatLine(role, content) {
  recentChatMessages.push({ role, content });
  if (recentChatMessages.length > 4) {
    recentChatMessages.shift();
  }
  renderChatMessages();
}

function resizeRenderer() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / Math.max(height, 1);
  camera.updateProjectionMatrix();
}

function clearCurrentModel() {
  animationLayer.clear();
  if (currentModel) {
    scene.remove(currentModel);
    currentModel = null;
  }
  interactionStatusNode.textContent = NO_MODEL_INTERACTION_STATUS;
  setResultPlaceholder("尚未生成资源。提交任务后可填充查看器，也可以先停留在这里观察处理中状态。");
}

function getSelectedModelSource() {
  const { value: resourceType } = resourceTypeSelect;
  const { urlInput, localSource } = getResourceInputs(resourceType);

  if (localSource.objectUrl) {
    return {
      resourceType,
      kind: "local-file",
      fileName: localSource.fileName,
      url: localSource.objectUrl,
    };
  }

  return {
    resourceType,
    kind: "remote-url",
    url: urlInput.value.trim(),
  };
}

function isGlbFile(file) {
  return file.name.toLowerCase().endsWith(".glb");
}

function handleModelFileChange(resourceType) {
  const { fileInput, urlInput, localSource } = getResourceInputs(resourceType);
  const file = fileInput.files?.[0];

  clearLocalObjectUrl(localSource);

  if (!file) {
    setStatus(`${formatResourceLabel(resourceType)}本地文件已清除。`);
    return;
  }

  if (!isGlbFile(file)) {
    fileInput.value = "";
    setStatus("当前仅支持 GLB 格式。");
    return;
  }

  localSource.objectUrl = URL.createObjectURL(file);
  localSource.fileName = file.name;
  urlInput.value = "";
  setStatus(`已选择本地${formatResourceLabel(resourceType)}模型：${file.name}`);
}

function handleUrlInput(resourceType) {
  const { urlInput } = getResourceInputs(resourceType);
  if (!urlInput.value.trim()) {
    return;
  }
  clearResourceFileSelection(resourceType);
}

function buildLoaderUrl(modelSource) {
  if (modelSource.kind === "local-file") {
    return modelSource.url;
  }
  return `/api/proxy/glb?url=${encodeURIComponent(modelSource.url)}`;
}

function hydrateFormFromTask(task) {
  const profile = task.input_profile || {};
  const styleProfile = profile.style_profile || {};
  const extraPayload = profile.extra_payload || {};

  displayNameInput.value = profile.display_name || "";
  genderInput.value = profile.gender || "";
  birthLocationInput.value = profile.birth_location || "";
  birthDateTimeInput.value = (
    profile.birth_datetime ||
    extraPayload.birth_datetime ||
    ""
  ).slice(0, 16);
  referenceImageUrlInput.value = profile.reference_image_url || "";
  fashionStyleInput.value = styleProfile.fashion_style || "";
  spiritStyleInput.value = styleProfile.spirit_style || "";
  extraNoteInput.value = extraPayload.free_text || "";
  renderChatMessages();
}

async function restoreTaskFromNavigation() {
  const taskId = initialParams.get("taskId");
  if (!taskId || !authToken) {
    return false;
  }

  try {
    const task = await fetchTask(authToken, taskId);
    window.localStorage.setItem("bazi3d.lastTaskId", String(task.id));
    hydrateFormFromTask(task);
    renderTaskState({
      status: task.status,
      taskId: task.id,
      hasAssets: Array.isArray(task.assets) && task.assets.length > 0,
    });
    syncAssetsToViewer(task.assets, {
      autoLoadCompletedCharacter: task.status === "completed",
    });
    if (task.status === "pending") {
      startTaskPolling(authToken, task.id);
    }
    return true;
  } catch (error) {
    setTaskStatusError("任务恢复失败。");
    taskMetaNode.textContent = `任务 #${taskId}`;
    taskHintNode.textContent =
      error.message || "无法恢复该任务，请从任务详情页重新进入。";
    console.error(error);
    return false;
  }
}

function hydrateViewerFromQuery() {
  const personUrl = initialParams.get("personUrl");
  const guardianUrl = initialParams.get("guardianUrl");
  const resourceType = initialParams.get("resourceType");

  if (personUrl) {
    personUrlInput.value = personUrl;
  }
  if (guardianUrl) {
    guardianUrlInput.value = guardianUrl;
  }
  if (resourceType === "person" || resourceType === "guardian") {
    resourceTypeSelect.value = resourceType;
  }

  if (personUrl || guardianUrl) {
  setStatus(`已从 URL 参数中选择${formatResourceLabel(resourceTypeSelect.value)}模型。`);
    hideResultPlaceholder();
    void loadSelectedModel();
  }
}

export async function loadSelectedModel() {
  const modelSource = getSelectedModelSource();
  const label = modelSource.resourceType;

  if (!modelSource.url) {
    setStatus(`请输入${formatResourceLabel(label)}的 GLB 地址。`);
    return;
  }

  setStatus(`正在加载${formatResourceLabel(label)}模型...`);
  const loaderUrl = buildLoaderUrl(modelSource);
  applySkyboxBackground(scene, textureLoader, skyboxUrlInput.value.trim());

  try {
    const gltf = await loader.loadAsync(loaderUrl);
    clearCurrentModel();
    currentModel = gltf.scene;
    scene.add(currentModel);
    animationLayer.bind(gltf);
    hideResultPlaceholder();
    setStatus(`${formatResourceLabel(label)}模型已加载。`);
  } catch (error) {
    clearCurrentModel();
    setStatus(`${formatResourceLabel(label)}模型加载失败。`);
    console.error(error);
  }
}

export function syncAssetsToViewer(
  assets,
  { autoLoadCompletedCharacter = false } = {},
) {
  if (!Array.isArray(assets) || assets.length === 0) {
    setResultPlaceholder("尚未生成资源。提交任务后可填充查看器，也可以先停留在这里观察处理中状态。");
    return;
  }

  const personAsset = assets.find((asset) => asset.type === "person");
  const guardianAsset = assets.find((asset) => asset.type === "guardian");

  if (personAsset?.url) {
    clearResourceFileSelection("person");
    personUrlInput.value = personAsset.url;
  }
  if (guardianAsset?.url) {
    clearResourceFileSelection("guardian");
    guardianUrlInput.value = guardianAsset.url;
  }

  if (autoLoadCompletedCharacter && personAsset?.url) {
    resourceTypeSelect.value = "person";
    hideResultPlaceholder();
    void loadSelectedModel();
    return;
  }

  const selectedAsset =
    resourceTypeSelect.value === "person" ? personAsset : guardianAsset;
  if (selectedAsset?.url) {
    hideResultPlaceholder();
    void loadSelectedModel();
    return;
  }

  setResultPlaceholder("任务已返回资源，但当前所选资源缺少可加载地址。");
}

export function startTaskPolling(token, taskId) {
  if (pollTimer) {
    window.clearInterval(pollTimer);
  }

  pollTimer = window.setInterval(async () => {
    try {
      const task = await fetchTask(token, taskId);
      renderTaskState({
        status: task.status,
        taskId: task.id,
        hasAssets: Array.isArray(task.assets) && task.assets.length > 0,
      });
      syncAssetsToViewer(task.assets, {
        autoLoadCompletedCharacter: task.status === "completed",
      });

      if (task.status === "completed" || task.status === "failed") {
        window.clearInterval(pollTimer);
        pollTimer = null;
      }
    } catch (error) {
      setTaskStatusError("任务轮询失败。");
      taskMetaNode.textContent = `任务 #${taskId}`;
      taskHintNode.textContent =
        "请求失败，轮询已停止。检查后端状态后可以再次尝试。";
      console.error(error);
      window.clearInterval(pollTimer);
      pollTimer = null;
    }
  }, 2000);
}

async function handleTaskSubmit(event) {
  event.preventDefault();

  const token = getStoredToken();
  if (!token) {
    handleUnauthorized();
    return;
  }

  const payload = {
    display_name: displayNameInput.value.trim(),
    gender: genderInput.value.trim(),
    birth_location: birthLocationInput.value.trim(),
    reference_image_url: referenceImageUrlInput.value.trim(),
    style_profile: {
      fashion_style: fashionStyleInput.value.trim(),
      spirit_style: spiritStyleInput.value.trim(),
    },
    extra_payload: {
      birth_datetime: birthDateTimeInput.value || null,
      free_text: extraNoteInput.value.trim(),
    },
  };

  renderTaskState({
    status: "submitting",
    note: "正在将任务内容提交到 `/api/tasks`，并准备结果区域的占位提示。",
  });

  try {
    const task = await createTask(token, payload);
    window.localStorage.setItem("bazi3d.lastTaskId", String(task.id));
    window.history.replaceState(null, "", `./index.html?taskId=${encodeURIComponent(task.id)}`);
    renderTaskState({
      status: task.status,
      taskId: task.id,
      hasAssets: Array.isArray(task.assets) && task.assets.length > 0,
    });
    startTaskPolling(token, task.id);
  } catch (error) {
    setTaskStatusError("任务创建失败。");
    taskMetaNode.textContent = "任务请求未能完成。";
    taskHintNode.textContent =
      error.message || "后端在创建任务前拒绝了本次请求。";
    console.error(error);
  }
}

function animate() {
  const delta = clock.getDelta();
  resizeRenderer();
  controls.update();
  animationLayer.update(delta);
  renderer.render(scene, camera);
  window.requestAnimationFrame(animate);
}

function bindStyleChipGroup(groupName, targetInput) {
  const options = document.querySelectorAll(`input[name="${groupName}"]`);
  options.forEach((option) => {
    option.addEventListener("change", () => {
      targetInput.value = option.value;
    });
  });
}

function resetCreateForm() {
  taskForm.reset();
  window.localStorage.removeItem("bazi3d.lastTaskId");
  window.history.replaceState(null, "", "./index.html");
  clearResourceFileSelection("person");
  clearResourceFileSelection("guardian");
  renderTaskState({
    status: "idle",
    note: "已重置表单。可以重新整理角色资料后再次提交。",
  });
  setStatus("请输入 GLB 地址或选择本地文件后加载模型。");
  recentChatMessages.length = 0;
  renderChatMessages();
  clearCurrentModel();
}


async function handleChatSend() {
  const token = getStoredToken();
  const message = chatInput.value.trim();

  if (!token) {
    handleUnauthorized();
    return;
  }
  if (!message) {
    setChatLogStatus("角色对话：请先输入消息。", { isError: true });
    return;
  }

  appendChatLine("user", message);
  chatInput.value = "";

  try {
    const response = await sendCharacterChat(token, {
      message,
      role: resourceTypeSelect.value,
      input_profile: {
        display_name: displayNameInput.value.trim(),
        gender: genderInput.value.trim(),
        birth_location: birthLocationInput.value.trim(),
        style_profile: {
          fashion_style: fashionStyleInput.value.trim(),
          spirit_style: spiritStyleInput.value.trim(),
        },
      },
      recent_messages: recentChatMessages.slice(-2),
    });
    appendChatLine("character", response.reply);
  } catch (error) {
    setChatLogStatus("角色对话失败。", { isError: true });
    console.error(error);
  }
}


if (!authToken) {
  throw new Error("Authentication redirect triggered.");
}

loadButton.addEventListener("click", () => {
  void loadSelectedModel();
});

personFileInput.addEventListener("change", () => {
  handleModelFileChange("person");
});

guardianFileInput.addEventListener("change", () => {
  handleModelFileChange("guardian");
});

personUrlInput.addEventListener("input", () => {
  handleUrlInput("person");
});

guardianUrlInput.addEventListener("input", () => {
  handleUrlInput("guardian");
});

resourceTypeSelect.addEventListener("change", () => {
  setStatus(`已选择${formatResourceLabel(resourceTypeSelect.value)}模型。`);
});

taskForm.addEventListener("submit", (event) => {
  void handleTaskSubmit(event);
});

resetTaskFormButton.addEventListener("click", () => {
  resetCreateForm();
});

displayNameInput.addEventListener("input", () => {
  renderChatMessages();
});

motionStatusNode.textContent = "伪动作系统：等待模型加载，模型将保持静止。";
interactionStatusNode.textContent = NO_MODEL_INTERACTION_STATUS;

playIdleButton.addEventListener("click", () => {
  animationLayer.playClip("idle");
});

playWaveButton.addEventListener("click", () => {
  animationLayer.playClip("wave");
});

triggerGreetButton.addEventListener("click", () => {
  animationLayer.playClip("greet");
});

sendChatButton.addEventListener("click", () => {
  void handleChatSend();
});

attachModelInteraction({
  canvas,
  camera,
  scene,
  getCurrentModel: () => currentModel,
});

bindStyleChipGroup("fashion-style-option", fashionStyleInput);
bindStyleChipGroup("spirit-style-option", spiritStyleInput);
renderTaskState({ status: "idle" });
renderChatMessages();
void restoreTaskFromNavigation().then((restored) => {
  if (!restored) {
    hydrateViewerFromQuery();
  }
});
animate();

