import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { OBJLoader } from "three/addons/loaders/OBJLoader.js";
import { MTLLoader } from "three/addons/loaders/MTLLoader.js";
import { Sky } from "three/addons/objects/Sky.js";


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
document.body.style.margin = "0";
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const dir = new THREE.DirectionalLight(0xffffff, 1.0);
dir.position.set(5, 10, 5);
scene.add(dir);

const controls = new OrbitControls(camera, renderer.domElement);

controls.target.set(
  1.2033503249851856,
  1.9279949403548189,
  -1.097272302029383
);

controls.update();

window.camera = camera;
window.controls = controls;

const sky = new Sky();
sky.scale.setScalar(300);
scene.add(sky);

const skyUniforms = sky.material.uniforms;

skyUniforms.turbidity.value = 8;
skyUniforms.rayleigh.value = 2;
skyUniforms.mieCoefficient.value = 0.005;
skyUniforms.mieDirectionalG.value = 0.8;


const sun = new THREE.Vector3();
sun.setFromSphericalCoords(
  1,
  THREE.MathUtils.degToRad(90),
  THREE.MathUtils.degToRad(120)
);

skyUniforms.sunPosition.value.copy(sun);




function loadObjMtl(basePath, objFile, mtlFile) {
  return new Promise((resolve, reject) => {
    const mtlLoader = new MTLLoader().setPath(basePath);
    mtlLoader.load(
      mtlFile,
      (materials) => {
        materials.preload();
        const objLoader = new OBJLoader()
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


async function init() {
  try {

    // notranjost avta - Nejla Perenda
    const cabinObj = await loadObjMtl(
      "/models/cabin/",
      "rac_grafika_model_armatura2.obj",
      "rac_grafika_model_armatura2.mtl"
    );
    scene.add(cabinObj);

    // control unit - Milos Avakumovic
    const controlBoxObj = await loadObjMtl(
      "/models/control_box/",
      "model_1.obj",
      "model_1.mtl"
    );
    cabinObj.add(controlBoxObj);

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
    standObj.position.set(1.33, 1.9, -0.6);
    standObj.rotation.set(0, 0, 0.9);
    standObj.scale.setScalar(1.3);    


  } catch (e) {
    console.error("Load error:", e);
  }
}



init();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

renderer.setAnimationLoop(() => {
  renderer.render(scene, camera);
});
