import * as THREE from "https://esm.sh/three@0.165.0";
import { OrbitControls } from "https://esm.sh/three@0.165.0/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "https://esm.sh/three@0.165.0/examples/jsm/loaders/GLTFLoader.js";
import { applySkyboxBackground } from "./skybox.js";
import { createAnimationLayer } from "./animation.js";
import { attachModelInteraction } from "./interaction.js";

export function createViewerRuntime({
  canvas,
  statusNode,
  motionStatusNode,
  interactionStatusNode,
  personUrlInput,
  guardianUrlInput,
  resourceTypeSelect,
  skyboxUrlInput,
}) {
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
  const animationLayer = createAnimationLayer(motionStatusNode);
  let currentModel = null;

  function formatResourceLabel(value) {
    return value === "guardian" ? "守护灵" : "人物";
  }

  function setStatus(message) {
    statusNode.textContent = message;
    statusNode.classList.remove("is-error");
  }

  function setStatusError(message) {
    statusNode.textContent = message;
    statusNode.classList.add("is-error");
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
  }

  function getSelectedUrl() {
    return resourceTypeSelect.value === "person"
      ? personUrlInput.value.trim()
      : guardianUrlInput.value.trim();
  }

  async function loadSelectedModel() {
    const url = getSelectedUrl();
    const label = resourceTypeSelect.value;

    if (!url) {
      setStatus(`请输入${formatResourceLabel(label)}的 GLB 地址。`);
      return;
    }

    setStatus(`正在加载${formatResourceLabel(label)}模型...`);
    applySkyboxBackground(scene, textureLoader, skyboxUrlInput.value.trim());

    try {
      const gltf = await loader.loadAsync(url);
      clearCurrentModel();
      currentModel = gltf.scene;
      scene.add(currentModel);
      animationLayer.bind(gltf);
      setStatus(`${formatResourceLabel(label)}模型已加载。`);
    } catch (error) {
      clearCurrentModel();
      setStatusError(`${formatResourceLabel(label)}模型加载失败。`);
      console.error(error);
    }
  }

  function syncAssetsToViewer(assets) {
    if (!Array.isArray(assets) || assets.length === 0) {
      return false;
    }

    const personAsset = assets.find((asset) => asset.type === "person");
    const guardianAsset = assets.find((asset) => asset.type === "guardian");

    if (personAsset?.url) {
      personUrlInput.value = personAsset.url;
    }
    if (guardianAsset?.url) {
      guardianUrlInput.value = guardianAsset.url;
    }

    const selectedAsset =
      resourceTypeSelect.value === "person" ? personAsset : guardianAsset;
    if (selectedAsset?.url) {
      void loadSelectedModel();
      return true;
    }

    return false;
  }

  function animate() {
    const delta = clock.getDelta();
    resizeRenderer();
    controls.update();
    animationLayer.update(delta);
    renderer.render(scene, camera);
    window.requestAnimationFrame(animate);
  }

  attachModelInteraction({
    canvas,
    camera,
    scene,
    getCurrentModel: () => currentModel,
    statusNode: interactionStatusNode,
  });

  animate();

  return {
    clearCurrentModel,
    loadSelectedModel,
    playClip: (presetName) => animationLayer.playClip(presetName),
    setStatus,
    setStatusError,
    syncAssetsToViewer,
  };
}
