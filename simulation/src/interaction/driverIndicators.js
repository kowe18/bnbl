import * as THREE from "three";

function firstMesh(obj) {
  if (!obj) return null;
  if (obj.isMesh) return obj;
  let found = null;
  obj.traverse((o) => { if (!found && o.isMesh) found = o; });
  return found;
}

function setEmissiveOrColor(mesh, hex, intensity = 1.5) {
  if (!mesh) return;
  const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];

  for (const m of mats) {
    if (!m) continue;
    if (m.emissive) {
      m.emissive.set(hex);
      m.emissiveIntensity = intensity;
    } else if (m.color) {
      m.color.set(hex);
    }
    m.needsUpdate = true;
  }
}

export function createDriverIndicators(root, { screenName, lampName }) {
  const screenObj = root.getObjectByName(screenName);
  const lampObj   = root.getObjectByName(lampName);

  // ako su Group, uzmi prvi mesh unutra
  const screen = firstMesh(screenObj);
  const lamp   = firstMesh(lampObj);

  console.log("screenObj:", screenObj?.name, "-> mesh:", screen?.name);
  console.log("lampObj:", lampObj?.name, "-> mesh:", lamp?.name);

  function applyDriverState(code) {
    console.log("applyDriverState:", code);

    if (code === "00") { // budan
      setEmissiveOrColor(lamp,   0x00ff00, 2.0);
      setEmissiveOrColor(screen, 0x003300, 2.5);
    }
    if (code === "01") { // utrujen
      setEmissiveOrColor(lamp,   0xffff00, 2.0);
      setEmissiveOrColor(screen, 0x333300, 2.5);
    }
    if (code === "10") { // zaspan
      setEmissiveOrColor(lamp,   0xff0000, 2.0);
      setEmissiveOrColor(screen, 0x330000, 2.5);
    }
  }

  return { applyDriverState };
}
