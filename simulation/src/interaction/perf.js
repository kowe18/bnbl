export function createPerfTracker() {
  const tStart = performance.now();
  let tModelsLoaded = null;
  let tFirstFrame = null;

  // FPS 
  let frameCount = 0;
  let fpsWindowStart = performance.now();
  let fpsAvg = 0;

  // WS 
  let wsCount = 0;
  let wsWindowStart = performance.now();
  let wsRate = 0;

  // HUD elemenenti
  const elLoading = document.getElementById("perf-loading");
  const elFirstFrame = document.getElementById("perf-firstframe");
  const elFps = document.getElementById("perf-fps");
  const elWs = document.getElementById("perf-ws");

  function ms(v) {
    return `${v.toFixed(0)} ms`;
  }

  function updateHud() {
    if (elLoading) {
      elLoading.textContent = `Loading: ${tModelsLoaded ? ms(tModelsLoaded - tStart) : "-"}`;
    }
    if (elFirstFrame) {
      elFirstFrame.textContent = `First frame: ${tFirstFrame ? ms(tFirstFrame - tStart) : "-"}`;
    }
    if (elFps) {
      elFps.textContent = `FPS(avg): ${fpsAvg ? fpsAvg.toFixed(1) : "-"}`;
    }
    if (elWs) {
      elWs.textContent = `WS msgs/s: ${wsRate ? wsRate.toFixed(1) : "0.0"}`;
    }
  }

  return {
    markModelsLoaded() {
      if (tModelsLoaded == null) {
        tModelsLoaded = performance.now();
        console.log("[PERF] Models loaded:", ms(tModelsLoaded - tStart));
        updateHud();
      }
    },

    markFirstFrame() {
      if (tFirstFrame == null) {
        tFirstFrame = performance.now();
        console.log("[PERF] First frame:", ms(tFirstFrame - tStart));
        updateHud();
      }
    },

    tickFrame() {
      frameCount++;
      const now = performance.now();
      const dt = now - fpsWindowStart;

      // vsakih 1000ms
      if (dt >= 1000) {
        fpsAvg = (frameCount * 1000) / dt;
        frameCount = 0;
        fpsWindowStart = now;
        updateHud();
      }
    },

    tickWsMessage() {
      wsCount++;
      const now = performance.now();
      const dt = now - wsWindowStart;

      // wsRate update 
      if (dt >= 1000) {
        wsRate = (wsCount * 1000) / dt;
        wsCount = 0;
        wsWindowStart = now;
        updateHud();
      }
    }
  };
}
