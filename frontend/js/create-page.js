import { createTask, getStoredToken } from "./api.js";
import { handleUnauthorized } from "./modules/auth-guard.js";

const form = document.getElementById("rule-input-form");
const displayNameInput = document.getElementById("display-name");
const genderInput = document.getElementById("gender");
const birthLocationInput = document.getElementById("birth-location");
const birthDateTimeInput = document.getElementById("birth-datetime");
const referenceImageUrlInput = document.getElementById("reference-image-url");
const fashionStyleInput = document.getElementById("fashion-style");
const spiritStyleInput = document.getElementById("spirit-style");
const profileSummaryNode = document.getElementById("profile-summary");
const styleSummaryNode = document.getElementById("style-summary");
const submitStatusNode = document.getElementById("submit-status");

const demoValues = {
  displayName: "Ling Yuan RealChain",
  gender: "female",
  birthLocation: "Shanghai",
  birthDateTime: "1995-06-15T09:30",
  referenceImageUrl: "https://example.com/reference.png",
  fashionStyle: "modern_casual, clean silhouette, teal jacket, white sneakers",
  spiritStyle: "eastern_classical, water light aura, balanced guardian motif",
};

function renderSummary() {
  profileSummaryNode.textContent = `${displayNameInput.value || "未命名"}，${genderInput.options[genderInput.selectedIndex]?.text || "不限定"}，出生地点 ${birthLocationInput.value || "未填写"}。`;
  styleSummaryNode.textContent = `外在风格：${fashionStyleInput.value || "未填写"}；内在气质：${spiritStyleInput.value || "未填写"}。`;
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
    },
  };
}

function applyDemoValues() {
  displayNameInput.value = demoValues.displayName;
  genderInput.value = demoValues.gender;
  birthLocationInput.value = demoValues.birthLocation;
  birthDateTimeInput.value = demoValues.birthDateTime;
  referenceImageUrlInput.value = demoValues.referenceImageUrl;
  fashionStyleInput.value = demoValues.fashionStyle;
  spiritStyleInput.value = demoValues.spiritStyle;
  renderSummary();
  submitStatusNode.textContent = "演示数据已恢复，可继续提交生成任务。";
}

async function handleSubmit(event) {
  event.preventDefault();
  const token = getStoredToken();
  if (!token) {
    handleUnauthorized();
    return;
  }

  submitStatusNode.textContent = "正在创建生成任务...";
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
  genderInput,
  birthLocationInput,
  birthDateTimeInput,
  referenceImageUrlInput,
  fashionStyleInput,
  spiritStyleInput,
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
