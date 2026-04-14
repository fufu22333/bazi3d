import * as THREE from "https://esm.sh/three@0.165.0";

export function applySkyboxBackground(scene, textureLoader, url) {
  if (!url) {
    scene.background = new THREE.Color(0xf3f3f3);
    return;
  }

  textureLoader.load(
    url,
    (texture) => {
      texture.mapping = THREE.EquirectangularReflectionMapping;
      scene.background = texture;
    },
    undefined,
    () => {
      scene.background = new THREE.Color(0xf3f3f3);
    }
  );
}