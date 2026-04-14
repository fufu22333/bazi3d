const INTERACTION_PROMPT = "悬停交互：请将鼠标移到模型上";
const NO_MODEL_PROMPT = "悬停交互：请先加载模型。";

export function createAnimationLayer({
  motionStatusNode,
  interactionStatusNode,
} = {}) {
  let hasModel = false;

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
    setMotionStatus("伪动作系统：等待模型加载。");
    setInteractionStatus(NO_MODEL_PROMPT);
  }

  function bind(gltf) {
    hasModel = Boolean(gltf?.scene);
    if (!hasModel) {
      clear();
      return;
    }

    setMotionStatus("伪动作系统：模型保持静止，可切换文字状态。");
    setInteractionStatus(INTERACTION_PROMPT);
  }

  function playClip(name) {
    if (!hasModel) {
      setMotionStatus("伪动作系统：请先加载模型。");
      setInteractionStatus(NO_MODEL_PROMPT);
      return false;
    }

    if (name === "idle") {
      setMotionStatus("伪动作系统：模型静止，当前状态为待机。");
      setInteractionStatus("待机中");
      return true;
    }

    if (name === "wave") {
      setMotionStatus("伪动作系统：模型静止，当前状态为挥手。");
      setInteractionStatus("正在挥手");
      return true;
    }

    if (name === "greet") {
      setMotionStatus("伪动作系统：模型静止，当前状态为打招呼。");
      setInteractionStatus("正在打招呼");
      return true;
    }

    return false;
  }

  function update() {
    if (!hasModel) {
      return;
    }
  }

  return {
    bind,
    clear,
    playClip,
    update,
  };
}
