import { createViewerRuntime } from "./viewer/runtime.js";

const params = new URLSearchParams(window.location.search);
const personUrlInput = document.getElementById("person-url");
const guardianUrlInput = document.getElementById("guardian-url");
const resourceTypeSelect = document.getElementById("resource-type");
const demoModelNode = document.getElementById("demo-model");

const personUrl = params.get("personUrl") || "";
const guardianUrl = params.get("guardianUrl") || "";
if (personUrl) {
  personUrlInput.value = personUrl;
}
if (guardianUrl) {
  guardianUrlInput.value = guardianUrl;
}
if (params.get("resourceType") === "guardian") {
  resourceTypeSelect.value = "guardian";
}

const viewerRuntime = createViewerRuntime({
  canvas: document.getElementById("viewer-canvas"),
  statusNode: document.getElementById("viewer-status"),
  motionStatusNode: document.getElementById("motion-status"),
  interactionStatusNode: document.getElementById("interaction-status"),
  personUrlInput,
  guardianUrlInput,
  resourceTypeSelect,
  skyboxUrlInput: document.getElementById("skybox-url"),
});

function hideDemoModelWhenRealUrlExists() {
  const hasUrl =
    resourceTypeSelect.value === "guardian"
      ? Boolean(guardianUrlInput.value.trim())
      : Boolean(personUrlInput.value.trim());
  demoModelNode.classList.toggle("is-hidden", hasUrl);
}

document.getElementById("load-model").addEventListener("click", () => {
  hideDemoModelWhenRealUrlExists();
  void viewerRuntime.loadSelectedModel();
});

document.getElementById("play-idle").addEventListener("click", () => {
  viewerRuntime.playClip("idle");
});

document.getElementById("play-wave").addEventListener("click", () => {
  viewerRuntime.playClip("wave");
});

resourceTypeSelect.addEventListener("change", hideDemoModelWhenRealUrlExists);
personUrlInput.addEventListener("input", hideDemoModelWhenRealUrlExists);
guardianUrlInput.addEventListener("input", hideDemoModelWhenRealUrlExists);

hideDemoModelWhenRealUrlExists();
