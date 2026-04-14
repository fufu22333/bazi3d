import { fetchWorks } from "./api.js";

const statusNode = document.getElementById("gallery-status");
const listNode = document.getElementById("gallery-list");

function buildViewerUrl(work) {
  const params = new URLSearchParams({
    personUrl: work.asset.url,
    resourceType: "person",
  });
  return `./index.html?${params.toString()}`;
}

function buildWorkDetailUrl(work) {
  return `./work.html?id=${work.id}`;
}

export function renderWorks(items) {
  listNode.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    statusNode.textContent = "暂时还没有公开作品。";
    return;
  }

  statusNode.textContent = `已加载 ${items.length} 个作品。`;

  items.forEach((work) => {
    const card = document.createElement("article");
    card.className = "work-card";

    const title = document.createElement("h2");
    title.textContent = work.title;

    const description = document.createElement("p");
    description.textContent = work.description || "暂无描述。";

    const link = document.createElement("a");
    link.href = buildViewerUrl(work);
    link.textContent = "在查看器中打开";

    const detailLink = document.createElement("a");
    detailLink.href = buildWorkDetailUrl(work);
    detailLink.textContent = "查看作品详情";

    card.append(title, description, link, detailLink);
    listNode.append(card);
  });
}

async function loadGallery() {
  try {
    const payload = await fetchWorks();
    renderWorks(payload.items);
  } catch (error) {
    statusNode.textContent = "加载作品失败。";
    console.error(error);
  }
}

void loadGallery();
