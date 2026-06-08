import { createTask, getStoredToken } from "./api.js";
import { handleUnauthorized } from "./modules/auth-guard.js";

const form = document.getElementById("rule-input-form");
const displayNameInput = document.getElementById("display-name");
const occasionInput = document.getElementById("occasion");
const relationshipInput = document.getElementById("relationship");
const genderInput = document.getElementById("gender");
const birthLocationInput = document.getElementById("birth-location");
const birthDateTimeInput = document.getElementById("birth-datetime");
const favoriteColorInput = document.getElementById("favorite-color");
const referenceImageUrlInput = document.getElementById("reference-image-url");
const giftMessageInput = document.getElementById("gift-message");
const fashionStyleInput = document.getElementById("fashion-style");
const spiritStyleInput = document.getElementById("spirit-style");
const extraNoteInput = document.getElementById("extra-note");
const profileSummaryNode = document.getElementById("profile-summary");
const styleSummaryNode = document.getElementById("style-summary");
const submitStatusNode = document.getElementById("submit-status");

const demoValues = {
  displayName: "Ling Yuan",
  occasion: "birthday",
  relationship: "friend",
  gender: "female",
  birthLocation: "Shanghai",
  birthDateTime: "1995-06-15T09:30",
  favoriteColor: "teal",
  referenceImageUrl: "https://example.com/reference.png",
  giftMessage: "愿你在新的一岁里保持明亮、笃定和自由。",
  fashionStyle: "elegant_collectible, clean silhouette, teal accent, stable standing pose",
  spiritStyle: "eastern_classical, water light aura, compact guardian ornament",
  extraNote: "温柔、观察力强、喜欢清爽层次。模型需要轮廓完整、结构稳定、适合 GLB 预览。",
};

function selectedText(selectNode) {
  return selectNode.options[selectNode.selectedIndex]?.text || "";
}

function renderSummary() {
  profileSummaryNode.textContent = `${displayNameInput.value || "未命名"}，${selectedText(relationshipInput) || "未填写"}，${selectedText(occasionInput) || "生日"}，出生城市 ${birthLocationInput.value || "未填写"}。`;
  styleSummaryNode.textContent = `主模型：${fashionStyleInput.value || "未填写"}；陪伴摆件：${spiritStyleInput.value || "未填写"}；偏好色：${favoriteColorInput.value || "未填写"}。`;
}

function bindStyleChipGroup(groupName, targetInput) {
  document.querySelectorAll(`input[name="${groupName}"]`).forEach((option) => {
    option.addEventListener("change", () => {
      targetInput.value = option.value;
      renderSummary();
    });
  });
}

function buildTaskPayload() {
  return {
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
      occasion: occasionInput.value.trim() || "birthday",
      relationship: relationshipInput.value.trim(),
      gift_message: giftMessageInput.value.trim(),
      favorite_color: favoriteColorInput.value.trim(),
      free_text: extraNoteInput.value.trim(),
    },
  };
}

function applyDemoValues() {
  displayNameInput.value = demoValues.displayName;
  occasionInput.value = demoValues.occasion;
  relationshipInput.value = demoValues.relationship;
  genderInput.value = demoValues.gender;
  birthLocationInput.value = demoValues.birthLocation;
  birthDateTimeInput.value = demoValues.birthDateTime;
  favoriteColorInput.value = demoValues.favoriteColor;
  referenceImageUrlInput.value = demoValues.referenceImageUrl;
  giftMessageInput.value = demoValues.giftMessage;
  fashionStyleInput.value = demoValues.fashionStyle;
  spiritStyleInput.value = demoValues.spiritStyle;
  extraNoteInput.value = demoValues.extraNote;
  renderSummary();
  submitStatusNode.textContent = "演示数据已恢复，可继续生成生日礼物模型。";
}

async function handleSubmit(event) {
  event.preventDefault();
  const token = getStoredToken();
  if (!token) {
    handleUnauthorized();
    return;
  }

  submitStatusNode.textContent = "正在创建生日礼物模型任务...";
  try {
    const task = await createTask(token, buildTaskPayload());
    window.localStorage.setItem("bazi3d.lastTaskId", String(task.id));
    submitStatusNode.textContent = `任务 #${task.id} 已创建，状态：${task.status}。`;
    window.location.href = `./task.html?taskId=${encodeURIComponent(task.id)}`;
  } catch (error) {
    submitStatusNode.textContent = error.message || "任务创建失败。";
  }
}

[
  displayNameInput,
  occasionInput,
  relationshipInput,
  genderInput,
  birthLocationInput,
  birthDateTimeInput,
  favoriteColorInput,
  referenceImageUrlInput,
  giftMessageInput,
  fashionStyleInput,
  spiritStyleInput,
  extraNoteInput,
].forEach((node) => {
  node.addEventListener("input", renderSummary);
  node.addEventListener("change", renderSummary);
});

bindStyleChipGroup("fashion-style-option", fashionStyleInput);
bindStyleChipGroup("spirit-style-option", spiritStyleInput);
document.getElementById("fill-demo").addEventListener("click", applyDemoValues);
form.addEventListener("submit", (event) => {
  void handleSubmit(event);
});

renderSummary();
