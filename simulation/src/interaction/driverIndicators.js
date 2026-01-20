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

function makeLedMaterial(mesh) {
  if (!mesh) return;
  const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];

  for (const m of mats) {
    if (!m) continue;

    m.toneMapped = false;

    if ("roughness" in m) m.roughness = Math.min(m.roughness, 0.45);
    if ("metalness" in m) m.metalness = Math.max(m.metalness, 0.05);

    m.needsUpdate = true;
  }
}


export function createDriverIndicators(root, { screenName, lampName }) {
  const screenObj = root.getObjectByName(screenName);
  const lampObj = root.getObjectByName(lampName);

  const screen = firstMesh(screenObj);
  const lamp = firstMesh(lampObj);

  makeLedMaterial(screen);
  makeLedMaterial(lamp);


  console.log("screenObj:", screenObj?.name, "-> mesh:", screen?.name);
  console.log("lampObj:", lampObj?.name, "-> mesh:", lamp?.name);

  const ledSpot = new THREE.SpotLight(0x00ff00, 0, 8.0, Math.PI / 7, 0.4, 2);
  ledSpot.castShadow = false;

  const target = new THREE.Object3D();

  if (lampObj) {
    lampObj.add(ledSpot);
    ledSpot.position.set(0, 1, 0.08);

    root.add(target);
    ledSpot.target = target;
  }

  const spill = new THREE.PointLight(0x00ff00, 0, 2.0);
  spill.decay = 2;
  if (lampObj) {
    lampObj.add(spill);
    spill.position.set(0, 0, 0.05);
  }

  function setDriverTargetWorld(worldPos) {
    if (!worldPos) return;
    const p = worldPos.clone();
    root.worldToLocal(p);
    target.position.copy(p);
    target.updateMatrixWorld(true);
  }

  function setLedState(hex, spotIntensity, spotDistance, emissiveIntensity) {
    setEmissiveOrColor(lamp, hex, emissiveIntensity);

    ledSpot.color.set(hex);
    ledSpot.intensity = spotIntensity;
    ledSpot.distance = spotDistance;

    spill.color.set(hex);
    spill.intensity = spotIntensity * 0.15;
    spill.distance = Math.max(1.0, spotDistance * 0.6);
  }

  ledSpot.intensity = 5.6;
  ledSpot.distance  = 3.8;
  ledSpot.decay     = 1.78;
  ledSpot.angle     = 0.56;
  ledSpot.penumbra  = 0.34;

  ledSpot.position.set(0.65, 1.69, -1.05);

  spill.intensity = 2.01;
  spill.distance  = 5.6;

  target.position.set(1.544497, 1.931363, -0.28992);

  setEmissiveOrColor(screen, 0x003300, 2.5);
  setLedState(0x00ff00, 18.0, 6.0, 2.8);
  ledSpot.intensity = 5.6;


  function applyDriverState(code) {
    if (code === "00") { // budan
      setEmissiveOrColor(screen, 0x003300, 2.5);
      setLedState(0x00ff00, 18.0, 6.0, 2.8);
      ledSpot.intensity = 5.6;
      return;
    }
    if (code === "01") { // utrujen
      setEmissiveOrColor(screen, 0x333300, 2.5);
      setLedState(0xffff00, 22.0, 6.5, 3.0);
      ledSpot.intensity = 10.6;
      return;
    }
    if (code === "10") { // zaspan
      setEmissiveOrColor(screen, 0x330000, 6.0);
      setLedState(0xff0000, 40.0, 7.0, 8.0);
      ledSpot.intensity = 15.6;
      return;
    }

    // off / unknown
    setEmissiveOrColor(screen, 0x000000, 0.0);
    setLedState(0x000000, 0.0, 2.0, 0.0);
    ledSpot.intensity = 5.6;
  }

  return { applyDriverState, setDriverTargetWorld, ledSpot, target, spill };

}
