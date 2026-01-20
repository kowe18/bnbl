export function attachStateInputDemo(onState) {
  window.addEventListener("keydown", (e) => {
    console.log("KEY:", e.key);
    if (e.key === "0") onState("00");
    if (e.key === "1") onState("01");
    if (e.key === "2") onState("10");
  });
}

