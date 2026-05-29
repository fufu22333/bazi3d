import { fetchTask, getStoredToken } from "./api.js";

const params = new URLSearchParams(window.location.search);
const taskIdInput = document.getElementById("task-id-input");
const taskTitleNode = document.getElementById("task-title");
const taskStatusNode = document.getElementById("task-status");
const statusLabelNode = document.getElementById("status-label");
const assetCountNode = document.getElementById("asset-count");
const timelineNode = document.getElementById("task-timeline");
const assetListNode = document.getElementById("asset-list");
let pollTimer = null;

const statusLabels = {
  pending: "处理中",
  completed: "完成",
  failed: "失败",
};

let demoStatus = params.get("demoStatus") === "pending" ? "pending" : "completed";

function resolveTaskId() {
  return (
    params.get("taskId") ||
    window.localStorage.getItem("bazi3d.lastTaskId") ||
    taskIdInput.value.trim()
  );
}

function updateReturnToCreateLink(taskId) {
  const homeLink = document.querySelector('[data-nav-link="home"]');
  if (!homeLink || !taskId) {
    return;
  }
  homeLink.href = `./index.html?taskId=${encodeURIComponent(taskId)}`;
}

function renderTimeline(status) {
  const items = [
    ["提交规则化输入", "前端将基础资料与风格画像提交到 /api/tasks。", "completed"],
    [
      "生成提示文本",
      "后端根据 input profile 组织人物与守护灵生成提示。",
      status === "failed" ? "idle" : "completed",
    ],
    [
      "返回模型资源",
      status === "completed"
        ? "任务完成后返回可供查看器加载的 GLB 资源地址。"
        : "任务处理中，模型资源仍在等待返回。",
      status === "completed" ? "completed" : "pending",
    ],
  ];

  timelineNode.replaceChildren(
    ...items.map(([title, detail, state]) => {
      const item = document.createElement("article");
      item.className = "timeline-item";
      const dot = document.createElement("span");
      dot.className = `dot ${state === "pending" ? "is-pending" : state === "idle" ? "is-idle" : ""}`;
      const body = document.createElement("div");
      const heading = document.createElement("h3");
      const paragraph = document.createElement("p");
      paragraph.className = "muted";
      heading.textContent = title;
      paragraph.textContent = detail;
      body.append(heading, paragraph);
      item.append(dot, body);
      return item;
    }),
  );
}

function renderAssets(assets = []) {
  if (!assets.length) {
    assetListNode.innerHTML = `
      <article class="asset-card">
        <h3>等待资源</h3>
        <p class="muted">当前任务尚未返回可展示的模型资源。</p>
      </article>
    `;
    return;
  }

  assetListNode.replaceChildren(
    ...assets.map((asset) => {
      const card = document.createElement("article");
      card.className = "asset-card";
      const title = document.createElement("h3");
      const detail = document.createElement("p");
      const link = document.createElement("a");
      detail.className = "muted";
      title.textContent = asset.type === "guardian" ? "守护灵模型" : "人物模型";
      detail.textContent = `${asset.file_format || "glb"} - ${asset.url || "暂无资源地址"}`;
      if (asset.url) {
        link.href = `./viewer.html?personUrl=${encodeURIComponent(asset.url)}`;
        link.textContent = "在模型查看页打开";
      }
      card.append(title, detail);
      if (asset.url) {
        card.append(link);
      }
      return card;
    }),
  );
}

function renderTask(task) {
  const assets = Array.isArray(task.assets) ? task.assets : [];
  taskIdInput.value = task.id || resolveTaskId();
  window.localStorage.setItem("bazi3d.lastTaskId", String(taskIdInput.value));
  updateReturnToCreateLink(taskIdInput.value);
  taskTitleNode.textContent = `任务 #${taskIdInput.value}`;
  taskStatusNode.textContent = `当前状态：${statusLabels[task.status] || task.status || "未知"}。`;
  statusLabelNode.textContent = statusLabels[task.status] || "未知";
  assetCountNode.textContent = String(assets.length);
  renderTimeline(task.status || "pending");
  renderAssets(assets);
}

function stopTaskPolling() {
  if (!pollTimer) {
    return;
  }
  window.clearInterval(pollTimer);
  pollTimer = null;
}

function startTaskPolling(taskId, token) {
  stopTaskPolling();
  pollTimer = window.setInterval(async () => {
    try {
      const task = await fetchTask(token, taskId);
      renderTask(task);
      if (task.status === "completed" || task.status === "failed") {
        stopTaskPolling();
      }
    } catch (error) {
      stopTaskPolling();
      taskStatusNode.textContent = error.message || "任务轮询失败。";
    }
  }, 2000);
}

function renderDemoTask() {
  renderTask({
    id: resolveTaskId() || 13,
    status: demoStatus,
    assets:
      demoStatus === "completed"
        ? [
            { type: "person", file_format: "glb", url: "character.glb" },
            { type: "guardian", file_format: "glb", url: "guardian.glb" },
          ]
        : [],
  });
}

async function loadTask() {
  const taskId = resolveTaskId();
  const token = getStoredToken();

  if (!taskId || !token) {
    renderDemoTask();
    return;
  }

  taskStatusNode.textContent = `正在查询任务 #${taskId}...`;
  try {
    const task = await fetchTask(token, taskId);
    renderTask(task);
    if (task.status === "pending") {
      startTaskPolling(task.id, token);
    } else {
      stopTaskPolling();
    }
  } catch (error) {
    taskStatusNode.textContent = error.message || "任务查询失败，已显示演示状态。";
    renderDemoTask();
  }
}

taskIdInput.value = resolveTaskId() || "13";
document.getElementById("load-task").addEventListener("click", () => {
  void loadTask();
});
document.getElementById("toggle-demo-status").addEventListener("click", () => {
  demoStatus = demoStatus === "completed" ? "pending" : "completed";
  renderDemoTask();
});

void loadTask();
