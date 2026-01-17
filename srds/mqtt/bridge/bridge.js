import mqtt from "mqtt";
import { WebSocketServer } from "ws";

const MQTT_URL = process.env.MQTT_URL || "mqtt://mosquitto:1883";
const TOPIC = process.env.MQTT_TOPIC || "/fatigue";

const wss = new WebSocketServer({ port: 3001 });
console.log("WS: ws://0.0.0.0:3001");
console.log("MQTT:", MQTT_URL, "TOPIC:", TOPIC);

const m = mqtt.connect(MQTT_URL);

m.on("connect", () => {
  console.log("Connected to MQTT");
  m.subscribe(TOPIC);
});

m.on("message", (_topic, payload) => {
  const text = payload.toString();
  for (const ws of wss.clients) {
    if (ws.readyState === ws.OPEN) ws.send(text);
  }
});
