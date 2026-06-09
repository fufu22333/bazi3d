import { fetchWorks } from "./api.js";

const statusNode = document.getElementById("gallery-status");
const listNode = document.getElementById("gallery-list");

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

function buildWorkDetailUrl(work) {
  return `./work.html?id=${work.id}`;
}

function createPreview(work) {
  const preview = document.createElement("div");
  preview.className = "work-preview";
  preview.setAttribute("aria-hidden", "true");

  const thumbnailUrl = work.asset?.metadata?.thumbnail_url;
  if (thumbnailUrl && work.asset?.metadata?.thumbnail_available !== false) {
    const image = document.createElement("img");
    image.src = thumbnailUrl;
    image.alt = "";
    image.loading = "lazy";
    image.addEventListener("error", () => {
      image.remove();
      preview.classList.remove("has-thumbnail");
      preview.classList.add("is-unavailable");
    });
    preview.append(image);
    preview.classList.add("has-thumbnail");
  } else if (work.asset?.is_available === false) {
    preview.classList.add("is-unavailable");
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
  title.textContent = work.title || "未命名礼物模型";

  const description = document.createElement("p");
  description.className = "muted";
  description.textContent = work.description || "暂无礼物模型描述。";

  const meta = document.createElement("div");
  meta.className = "work-meta";
  const occasion = work.asset?.metadata?.occasion || work.extra_payload?.occasion || "birthday";
  const occasionLabel = occasion === "birthday" ? "生日礼物" : "纪念礼物";
  meta.textContent = `${occasionLabel} · 可见性：${formatVisibility(work.visibility)}`;

  const actions = document.createElement("div");
  actions.className = "work-actions";

  if (work.asset?.is_available !== false && work.asset?.url) {
    const viewerLink = document.createElement("a");
    viewerLink.href = buildViewerUrl(work);
    viewerLink.textContent = "预览礼物模型";
    actions.append(viewerLink);

    const downloadLink = document.createElement("a");
    downloadLink.href = work.asset.url;
    downloadLink.download = `${work.title || "bazi3d-model"}.glb`;
    downloadLink.textContent = "下载 GLB";
    actions.append(downloadLink);
  }

  const detailLink = document.createElement("a");
  detailLink.href = buildWorkDetailUrl(work);
  detailLink.textContent = "查看礼物详情";

  actions.append(detailLink);
  card.append(preview, title, description, meta, actions);
  return card;
}

export function renderWorks(items) {
  listNode.innerHTML = "";
  listNode.classList.add("gallery-grid");

  if (!Array.isArray(items) || items.length === 0) {
    statusNode.textContent = "暂无公开礼物模型。";
    return;
  }

  statusNode.textContent = `已加载 ${items.length} 个公开礼物模型。`;

  items.forEach((work) => {
    listNode.append(createWorkCard(work));
  });
}

async function loadGallery() {
  try {
    const payload = await fetchWorks();
    renderWorks(payload.items);
  } catch {
    statusNode.textContent = "暂时没有可展示的公开礼物模型，可先查看演示作品详情。";
    listNode.classList.remove("gallery-grid");
    listNode.innerHTML = "";
    const fallback = document.createElement("article");
    fallback.className = "work-card";
    const title = document.createElement("h2");
    const detail = document.createElement("p");
    const actions = document.createElement("div");
    const link = document.createElement("a");
    detail.className = "muted";
    actions.className = "work-actions";
    title.textContent = "演示礼物模型";
    detail.textContent = "本地演示环境没有公开作品时，可以查看预置的生日礼物模型详情页。";
    link.href = "./work.html?demo=1";
    link.textContent = "查看演示详情";
    actions.append(link);
    fallback.append(title, detail, actions);
    listNode.append(fallback);
  }
}

void loadGallery();
