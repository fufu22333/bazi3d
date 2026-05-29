import { fetchWorks } from "./api.js";

const statusNode = document.getElementById("gallery-status");
const listNode = document.getElementById("gallery-list");

function buildViewerUrl(work) {
  const params = new URLSearchParams({
    personUrl: work.asset?.url || "",
    resourceType: "person",
    autoload: "1",
  });
  return `./viewer.html?${params.toString()}`;
}

function buildWorkDetailUrl(work) {
  return `./work.html?id=${work.id}`;
}

function createPreview(work) {
  const preview = document.createElement("div");
  preview.className = "work-preview";
  preview.setAttribute("aria-hidden", "true");

  const thumbnailUrl = work.asset?.metadata?.thumbnail_url;
  if (thumbnailUrl) {
    const image = document.createElement("img");
    image.src = thumbnailUrl;
    image.alt = "";
    image.loading = "lazy";
    preview.append(image);
    preview.classList.add("has-thumbnail");
  }

  return preview;
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

function createWorkCard(work) {
  const card = document.createElement("article");
  card.className = "work-card";

  const preview = createPreview(work);

  const title = document.createElement("h2");
  title.textContent = work.title || "未命名作品";

  const description = document.createElement("p");
  description.className = "muted";
  description.textContent = work.description || "暂无作品描述。";

  const meta = document.createElement("div");
  meta.className = "work-meta";
  meta.textContent = `可见性：${formatVisibility(work.visibility)}`;

  const actions = document.createElement("div");
  actions.className = "work-actions";

  const viewerLink = document.createElement("a");
  viewerLink.href = buildViewerUrl(work);
  viewerLink.textContent = "打开查看器";

  const detailLink = document.createElement("a");
  detailLink.href = buildWorkDetailUrl(work);
  detailLink.textContent = "查看详情";

  actions.append(viewerLink, detailLink);
  card.append(preview, title, description, meta, actions);
  return card;
}

export function renderWorks(items) {
  listNode.innerHTML = "";
  listNode.classList.add("gallery-grid");

  if (!Array.isArray(items) || items.length === 0) {
    statusNode.textContent = "暂无公开作品。";
    return;
  }

  statusNode.textContent = `已加载 ${items.length} 个公开作品。`;

  items.forEach((work) => {
    listNode.append(createWorkCard(work));
  });
}

async function loadGallery() {
  try {
    const payload = await fetchWorks();
    renderWorks(payload.items);
  } catch (error) {
    statusNode.textContent = "加载公开作品失败。";
    console.error(error);
  }
}

void loadGallery();
