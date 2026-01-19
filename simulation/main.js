import { createPerfTracker } from "./src/interaction/perf.js";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { OBJLoader } from "three/addons/loaders/OBJLoader.js";
import { MTLLoader } from "three/addons/loaders/MTLLoader.js";
import { Sky } from "three/addons/objects/Sky.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import Stats from "three/addons/libs/stats.module.js";
import { GUI } from "three/addons/libs/lil-gui.module.min.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";


import { createDriverIndicators } from "./src/interaction/driverIndicators.js";
import { attachStateInputDemo } from "./src/interaction/stateInputDemo.js";

const loadingManager = new THREE.LoadingManager();
const progressBar = document.getElementById('progress-fill');
const loadingText = document.getElementById('loading-text');
const loadingScreen = document.getElementById('loading-screen');
const perf = createPerfTracker();


let controlBoxObj = null;
let indicators = null;
let itemsLoaded = 0;
let itemsTotal = 0;

const clock = new THREE.Clock();
const mixers = [];
const birds = [];

const birdsMotion = {
  zMin: -80,
  zMax:  80,
  speed: 5,
  x: 70,
  y: 20
};


loadingManager.onStart = (url, loaded, total) => {
  itemsTotal = total;
  console.log(`Loading started: ${loaded}/${total}`);
};

loadingManager.onProgress = (url, loaded, total) => {
  itemsLoaded = loaded;
  const progress = (loaded / total) * 100;
  progressBar.style.width = progress + '%';
  loadingText.textContent = `Loading models... ${loaded}/${total}`;
};

loadingManager.onLoad = () => {
  console.log('All models loaded!');
  perf.markModelsLoaded();

  loadingText.textContent = 'Complete!';
  setTimeout(() => {
    loadingScreen.classList.add('hidden');
  }, 500);
};


loadingManager.onError = (url) => {
  console.error('Error loading:', url);
  loadingText.textContent = 'Error loading models';
};

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xFFFFFF);

const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  5000
);

camera.position.set(
    -0.18899407746813313, 
    2.4427262921372375, 
    -1.120140483793434
);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.style.margin = "0";
document.body.appendChild(renderer.domElement);

renderer.setPixelRatio(window.devicePixelRatio);

renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.5, // strength 
  0.15, // radius
  0.75 // threshold 
);
composer.addPass(bloomPass);
composer.addPass(new OutputPass());

window.bloomPass = bloomPass;


// Stats monitor (FPS counter)
const stats = new Stats();
stats.dom.style.position = 'fixed';
stats.dom.style.bottom = '0px';
stats.dom.style.top = 'auto';
document.body.appendChild(stats.dom);
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);

const dir = new THREE.DirectionalLight(0xffffff, 1.0);
dir.position.set(5, 10, 5);

dir.castShadow = true;

// kvaliteta sence
dir.shadow.mapSize.set(2048, 2048);

// Shadow-camera frustum 
dir.shadow.camera.near = 0.5;
dir.shadow.camera.far = 200;

dir.shadow.camera.left = -80;
dir.shadow.camera.right = 80;
dir.shadow.camera.top = 80;
dir.shadow.camera.bottom = -80;

// pomaga proti “acne”/črtam
dir.shadow.bias = -0.0005;

scene.add(dir);


// DEBUG: pokaže območje, kjer se sence sploh računajo
//const dirShadowHelper = new THREE.CameraHelper(dir.shadow.camera);
//scene.add(dirShadowHelper);

const controls = new OrbitControls(camera, renderer.domElement);

controls.target.set(
  1.2033503249851856,
  1.9279949403548189,
  -1.097272302029383
);

controls.update();

window.camera = camera;
window.controls = controls;

// zakomentarises za otkljucanu kameru odavdje :

controls.enableRotate = false;
controls.enableZoom = false;
controls.enablePan = false;
controls.enabled = false;

const fixedCamPos = camera.position.clone();

const head = {
  yaw0: 0,
  pitch0: 0,
  yaw: 0,
  pitch: 0,
  sensitivity: 0.002,

  maxYaw: THREE.MathUtils.degToRad(15),
  maxPitch: THREE.MathUtils.degToRad(10),
};

function initHeadFromCurrentView() {
  const startDir = new THREE.Vector3();
  camera.getWorldDirection(startDir);

  head.yaw0 = Math.atan2(startDir.x, startDir.z);
  head.pitch0 = Math.asin(THREE.MathUtils.clamp(startDir.y, -1, 1));

  head.yaw = 0;
  head.pitch = 0;
}

initHeadFromCurrentView();

let mouseActive = false;

renderer.domElement.addEventListener("mousedown", () => {
  mouseActive = true;
});

window.addEventListener("mouseup", () => {
  mouseActive = false;
});

window.addEventListener("mousemove", (e) => {
  if (!mouseActive) return;

  head.yaw   -= e.movementX * head.sensitivity;
  head.pitch -= e.movementY * head.sensitivity;

  head.yaw = THREE.MathUtils.clamp(head.yaw, -head.maxYaw, head.maxYaw);
  head.pitch = THREE.MathUtils.clamp(head.pitch, -head.maxPitch, head.maxPitch);
});

window.addEventListener("keydown", (e) => {
  if (e.code === "KeyR") {
    head.yaw = 0;
    head.pitch = 0;
  }
});

const _lookDir = new THREE.Vector3();

function applyHeadLookEachFrame() {
  camera.position.copy(fixedCamPos);

  const yaw = head.yaw0 + head.yaw;
  const pitch = head.pitch0 + head.pitch;

  _lookDir.set(
    Math.sin(yaw) * Math.cos(pitch),
    Math.sin(pitch),
    Math.cos(yaw) * Math.cos(pitch)
  );

  camera.lookAt(
    camera.position.x + _lookDir.x,
    camera.position.y + _lookDir.y,
    camera.position.z + _lookDir.z
  );
}

// do ovdje

const sky = new Sky();
sky.scale.setScalar(300);
scene.add(sky);

const skyUniforms = sky.material.uniforms;

skyUniforms.turbidity.value = 8;
skyUniforms.rayleigh.value = 2;
skyUniforms.mieCoefficient.value = 0.003;
skyUniforms.mieDirectionalG.value = 0.8;


const sun = new THREE.Vector3();
sun.setFromSphericalCoords(
  1,
  THREE.MathUtils.degToRad(91),
  THREE.MathUtils.degToRad(100)
);

skyUniforms.sunPosition.value.copy(sun);

// GUI Controls
const gui = new GUI();
gui.title('Scene Controls');

const effectsFolder = gui.addFolder('Effects');

const bloomSettings = {
  enabled: true
};

effectsFolder
  .add(bloomSettings, 'enabled')
  .name('Bloom')
  .onChange((v) => {
    bloomPass.enabled = v;
  });


const lightingFolder = gui.addFolder('Lighting');
lightingFolder.add(ambientLight, 'intensity', 0, 2, 0.1).name('Ambient Light');
lightingFolder.add(dir, 'intensity', 0, 3, 0.1).name('Directional Light');

const skyFolder = gui.addFolder('Sky');
skyFolder.add(skyUniforms.turbidity, 'value', 0, 20, 0.1).name('Turbidity');
skyFolder.add(skyUniforms.rayleigh, 'value', 0, 4, 0.1).name('Rayleigh');
skyFolder.add(skyUniforms.mieCoefficient, 'value', 0, 0.1, 0.001).name('Mie Coefficient');


const cameraFolder = gui.addFolder('Camera');
const cameraPresets = {
  'Driver View': () => {
    animateCamera(
      new THREE.Vector3(-0.18899407746813313, 2.4427262921372375, -1.120140483793434),
      new THREE.Vector3(1.2033503249851856, 1.9279949403548189, -1.097272302029383)
    );
  },
  'Exterior View': () => {
    animateCamera(
      new THREE.Vector3(-5, 3, 5),
      new THREE.Vector3(0, 0, 0)
    );
  },
  'Top View': () => {
    animateCamera(
      new THREE.Vector3(0, 10, 0),
      new THREE.Vector3(0, 0, 0)
    );
  }
};
cameraFolder.add(cameraPresets, 'Driver View');
cameraFolder.add(cameraPresets, 'Exterior View');
cameraFolder.add(cameraPresets, 'Top View');

// Raycaster for click interactions
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const infoPanel = document.getElementById('info-panel');
const infoContent = document.getElementById('info-content');

function onMouseClick(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children, true);

  if (intersects.length > 0) {
    const object = intersects[0].object;
    showObjectInfo(object);
  } else {
    infoPanel.classList.remove('visible');
  }
}

function showObjectInfo(object) {
  let info = `<strong>Name:</strong> ${object.name || 'Unnamed'}<br>`;
  info += `<strong>Type:</strong> ${object.type}<br>`;
  info += `<strong>Position:</strong> (${object.position.x.toFixed(2)}, ${object.position.y.toFixed(2)}, ${object.position.z.toFixed(2)})<br>`;
  
  if (object.material) {
    info += `<strong>Material:</strong> ${object.material.name || 'Default'}<br>`;
  }
  
  infoContent.innerHTML = info;
  infoPanel.classList.add('visible');
}

window.addEventListener('click', onMouseClick);

// Smooth camera animation
function animateCamera(targetPosition, targetLookAt) {
  const startPos = camera.position.clone();
  const startTarget = controls.target.clone();
  const duration = 1500;
  const startTime = Date.now();

  function animate() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = easeInOutCubic(progress);

    camera.position.lerpVectors(startPos, targetPosition, eased);
    controls.target.lerpVectors(startTarget, targetLookAt, eased);
    controls.update();

    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  }

  animate();
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function loadGLB(path) {
  return new Promise((resolve, reject) => {
    const loader = new GLTFLoader(loadingManager);
    loader.load(
      path,
      (gltf) => resolve(gltf.scene),
      undefined,
      (err) => reject(err)
    );
  });
}

function loadGLTF(path) {
  return new Promise((resolve, reject) => {
    const loader = new GLTFLoader(loadingManager);
    loader.load(path, (gltf) => resolve(gltf), undefined, (err) => reject(err));
  });
}



function loadObjMtl(basePath, objFile, mtlFile) {
  return new Promise((resolve, reject) => {
    const mtlLoader = new MTLLoader(loadingManager).setPath(basePath);
    mtlLoader.load(
      mtlFile,
      (materials) => {
        materials.preload();
        const objLoader = new OBJLoader(loadingManager)
          .setMaterials(materials)
          .setPath(basePath);

        objLoader.load(
          objFile,
          (obj) => resolve(obj),
          undefined,
          (err) => reject(err)
        );
      },
      undefined,
      (err) => reject(err)
    );
  });
}

function enableShadows(obj, { cast = true, receive = true } = {}) {
  if (!obj) return;
  obj.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = cast;
      o.receiveShadow = receive;
      // če so teksture čudne, ne rabimo tu nič več
    }
  });
}


async function init() {
  try {

    // notranjost avta - Nejla Perenda
    const cabinObj = await loadObjMtl(
      "/models/cabin/",
      "rac_grafika_model_armatura2.obj",
      "rac_grafika_model_armatura2.mtl"
    );
    scene.add(cabinObj);
    enableShadows(cabinObj, { cast: true, receive: true });


    // control unit - Milos Avakumovic
    controlBoxObj = await loadObjMtl(
      "/models/control_box/",
      "model_1.obj",
      "model_1.mtl"
    );
    cabinObj.add(controlBoxObj);
    enableShadows(controlBoxObj, { cast: true, receive: true });

    controlBoxObj.position.set(2.9, -1.42, -1.7);
    controlBoxObj.rotation.set(0, Math.PI, 0); 
    controlBoxObj.scale.setScalar(2);

    // camera - Vedran Dojcinovic
    const cameraModelObj = await loadObjMtl(
      "/models/camera/",
      "bnbl_camera.obj",
      "bnbl_camera.mtl"
    );
    cabinObj.add(cameraModelObj);
    enableShadows(cameraModelObj, { cast: true, receive: true });

    cameraModelObj.position.set(1.88, 1.67, -0.5);
    cameraModelObj.rotation.set(0, 10, 0);
    cameraModelObj.scale.setScalar(0.1);

    // camera stand - Sladjana Petrovic
    const standObj = await loadObjMtl(
      "/models/stand/",
      "proj.obj",
      "proj.mtl"
    );
    cabinObj.add(standObj);
    enableShadows(standObj, { cast: true, receive: true });

    standObj.position.set(1.33, 1.9, -0.6);
    standObj.rotation.set(0, 0, 0.9);
    standObj.scale.setScalar(1.3);    

    // mesto - Elbolillo (https://www.fab.com/sellers/Elbolillo)
    const busStop = await loadGLB("/models/city/bus_stop.glb");
    scene.add(busStop);
    enableShadows(busStop, { cast: true, receive: true });


    busStop.position.set(0, -1.5, 28);
    busStop.rotation.set(0, 0, 0);
    busStop.scale.setScalar(1.7);

    // roke - DJMaesen
    const arms = await loadGLB("/models/arms/cartoon_fps_arms.glb");
    scene.add(arms);
    enableShadows(arms, { cast: true, receive: true });


    arms.position.set(0.67, 1.7, -1.1);
    arms.rotation.set(0, 1.5, 0);
    arms.scale.setScalar(0.0015);

    // ptice - https://sketchfab.com/moizmuhammad373
    const birdsGltf = await loadGLTF("/models/birds/bird.glb");
    const flock = birdsGltf.scene;
    scene.add(flock);

    flock.position.set(0, 25, 0);
    flock.scale.setScalar(3);
    flock.rotation.set(0, 0, 0);

    if (birdsGltf.animations && birdsGltf.animations.length > 0) {
      const mixer = new THREE.AnimationMixer(flock);
      mixer.clipAction(birdsGltf.animations[0]).play();
      mixers.push(mixer);
    }
    birds.push(flock);

    
    indicators = createDriverIndicators(controlBoxObj, {
    screenName: "Ekran_Material.004",
    lampName: "LED_trak_LED_bar",
    });

    indicators.setDriverTargetWorld(camera.position);

  } catch (e) {
    console.error("Load error:", e);
  }
}
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:3001";

// WebSocket real-time data iz Dockera
const connectionStatus = document.getElementById("connection-status");
let ws;

function connectWebSocket() {
  try {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log("WS OPEN", WS_URL);
      connectionStatus.textContent = `WebSocket: Connected (${WS_URL})`;
      connectionStatus.className = "status-connected";
    };

    ws.onerror = (e) => {
      console.log("WS ERROR", e);
      connectionStatus.textContent = "WebSocket: Error";
      connectionStatus.className = "status-disconnected";
    };

    ws.onclose = () => {
      console.log("WS CLOSE");
      connectionStatus.textContent = "WebSocket: Disconnected";
      connectionStatus.className = "status-disconnected";
      setTimeout(connectWebSocket, 5000);
    };

    ws.onmessage = (e) => {
              perf.tickWsMessage();
      try {
        const msg = JSON.parse(e.data);
        const code = String(msg.status_code).trim();

        if (indicators) indicators.applyDriverState(code);
      } catch (err) {
        console.warn("Bad WS message:", e.data, err);
      }
    };
  } catch (err) {
    console.error("WebSocket connection failed:", err);
    connectionStatus.textContent = "WebSocket: Failed";
    connectionStatus.className = "status-disconnected";
  }
}


init().then(() => {
  connectWebSocket();
  attachStateInputDemo((code) => indicators?.applyDriverState(code));
});



controls.enableRotate = true;
controls.enableZoom = true;
controls.enablePan = true;

//init();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);

  composer.setSize(window.innerWidth, window.innerHeight);
  bloomPass.setSize(window.innerWidth, window.innerHeight);

});

renderer.setAnimationLoop(() => {
  const dt = clock.getDelta();

  for (const m of mixers) m.update(dt);

  for (const b of birds) {
    b.position.x = birdsMotion.x;
    b.position.y = birdsMotion.y;

    b.position.z += birdsMotion.speed * dt;

    if (b.position.z >= birdsMotion.zMax) {
      b.position.z = birdsMotion.zMin;
    }

    b.rotation.y = Math.PI;
  }


  applyHeadLookEachFrame(); 
  perf.markFirstFrame();
perf.tickFrame();

  stats.update();
  composer.render();
  

});


