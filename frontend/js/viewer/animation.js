const INTERACTION_PROMPT = "悬停交互：请将鼠标移到模型上";
const NO_MODEL_PROMPT = "悬停交互：请先加载模型。";

export function createAnimationLayer({
  motionStatusNode,
  interactionStatusNode,
} = {}) {
  let hasModel = false;
  let modelRoot = null;
  let activePreset = "idle";
  let elapsedTime = 0;
  const basePosition = { x: 0, y: 0, z: 0 };
  const baseRotation = { x: 0, y: 0, z: 0 };

  function setMotionStatus(message) {
    if (motionStatusNode) {
      motionStatusNode.textContent = message;
    }
  }

  function setInteractionStatus(message) {
    if (interactionStatusNode) {
      interactionStatusNode.textContent = message;
    }
  }

  function clear() {
    hasModel = false;
    modelRoot = null;
    activePreset = "idle";
    elapsedTime = 0;
    setMotionStatus("伪动作系统：等待模型加载。");
    setInteractionStatus(NO_MODEL_PROMPT);
  }

  function bind(gltf) {
    hasModel = Boolean(gltf?.scene);
    if (!hasModel) {
      clear();
      return;
    }

    modelRoot = gltf.scene;
    basePosition.x = modelRoot.position.x;
    basePosition.y = modelRoot.position.y;
    basePosition.z = modelRoot.position.z;
    baseRotation.x = modelRoot.rotation.x;
    baseRotation.y = modelRoot.rotation.y;
    baseRotation.z = modelRoot.rotation.z;
    activePreset = "idle";
    elapsedTime = 0;
    setMotionStatus("动作系统：待机轻微呼吸中，可切换摇摆。");
    setInteractionStatus(INTERACTION_PROMPT);
  }

  function playClip(name) {
    if (!hasModel) {
      setMotionStatus("伪动作系统：请先加载模型。");
      setInteractionStatus(NO_MODEL_PROMPT);
      return false;
    }

    if (name === "idle") {
      activePreset = "idle";
      elapsedTime = 0;
      setMotionStatus("动作系统：待机轻微呼吸中。");
      setInteractionStatus("待机中");
      return true;
    }

    if (name === "wave") {
      activePreset = "wave";
      elapsedTime = 0;
      setMotionStatus("动作系统：正在摇摆。");
      setInteractionStatus("正在摇摆");
      return true;
    }

    if (name === "greet") {
      activePreset = "wave";
      elapsedTime = 0;
      setMotionStatus("动作系统：正在摇摆。");
      setInteractionStatus("正在摇摆");
      return true;
    }

    return false;
  }

  function applyFallbackMotion(delta = 0) {
    if (!modelRoot) {
      return;
    }
    elapsedTime += delta;

    const bob = Math.sin(elapsedTime * 2.2) * 0.025;
    modelRoot.position.set(
      basePosition.x,
      basePosition.y + bob,
      basePosition.z,
    );

    if (activePreset === "wave") {
      modelRoot.rotation.set(
        baseRotation.x,
        baseRotation.y + Math.sin(elapsedTime * 6.5) * 0.22,
        baseRotation.z + Math.sin(elapsedTime * 9) * 0.08,
      );
      return;
    }

    modelRoot.rotation.set(
      baseRotation.x,
      baseRotation.y + Math.sin(elapsedTime * 0.9) * 0.035,
      baseRotation.z,
    );
  }

  function update(delta = 0) {
    if (!hasModel) {
      return;
    }
    applyFallbackMotion(delta);
  }

  return {
    bind,
    clear,
    playClip,
    update,
  };
}
