import * as THREE from "https://esm.sh/three@0.165.0";

export function attachModelInteraction({
  canvas,
  camera,
  scene,
  getCurrentModel,
  statusNode,
}) {
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let highlightedMesh = null;

  function updatePointer(event) {
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  }

  function getHits(model) {
    raycaster.setFromCamera(pointer, camera);
    return raycaster.intersectObject(model, true);
  }

  function clearHighlight() {
    if (highlightedMesh?.material?.emissive) {
      highlightedMesh.material.emissive.setHex(0x000000);
    }
    highlightedMesh = null;
  }

  function onPointerMove(event) {
    const model = getCurrentModel();
    if (!model) {
      if (statusNode) {
        statusNode.textContent = "悬停交互：请先加载模型。";
      }
      clearHighlight();
      return;
    }

    updatePointer(event);
    const hits = getHits(model);
    clearHighlight();

    if (hits.length > 0) {
      const hit = hits[0].object;
      if (hit.material?.emissive) {
        hit.material.emissive.setHex(0x2244aa);
        highlightedMesh = hit;
      }
    }
  }

  function onPointerDown(event) {
    const model = getCurrentModel();
    if (!model) {
      if (statusNode) {
        statusNode.textContent = "点击交互：请先加载模型。";
      }
      return;
    }

    updatePointer(event);
    const hits = getHits(model);

    if (hits.length > 0) {
      const hit = hits[0].object;
      if (hit.material?.emissive) {
        hit.material.emissive.setHex(0xaa5522);
        highlightedMesh = hit;
      }
    }
  }

  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerdown", onPointerDown);
}
