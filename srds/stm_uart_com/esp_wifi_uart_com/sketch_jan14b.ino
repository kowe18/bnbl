#include <WiFi.h>
#include <PubSubClient.h>

// WiFi
const char* WIFI_SSID = "iPhone: Vedran";
const char* WIFI_PASS = "vedran123";

// MQTT
const char* MQTT_HOST = "172.20.10.2";
const int   MQTT_PORT = 1883;
const char* SUB_TOPIC = "/fatigue";

static const int UART_RX = 20;  
static const int UART_TX = 21;  

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  Serial.print("MQTT RX [");
  Serial.print(topic);
  Serial.print("] ");

  for (unsigned int i = 0; i < length; i++) {
    char c = (char)payload[i];
    Serial.print(c);
    Serial1.write((uint8_t)c);
  }
  Serial.println();
  Serial1.write('\n');
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true, true);
  delay(200);

  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.print("[WiFi] connecting");
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
    if (millis() - t0 > 25000) {
      Serial.println("\n[WiFi] timeout -> reboot");
      delay(500);
      ESP.restart();
    }
  }

  Serial.println("\n[WiFi] OK");
  Serial.print("[WiFi] ESP IP: ");
  Serial.println(WiFi.localIP());
}

void connectMQTT() {
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
  mqtt.setSocketTimeout(5);

  while (!mqtt.connected()) {
    Serial.print("[MQTT] connecting to ");
    Serial.print(MQTT_HOST);
    Serial.print(":");
    Serial.print(MQTT_PORT);
    Serial.print(" ... ");

    String clientId = "esp32c6-uart-";
    clientId += String((uint32_t)ESP.getEfuseMac(), HEX);

    if (mqtt.connect(clientId.c_str())) {
      Serial.println("OK");
      mqtt.subscribe(SUB_TOPIC);
      Serial.print("[MQTT] subscribed: ");
      Serial.println(SUB_TOPIC);
    } else {
      Serial.print("FAIL state=");
      Serial.println(mqtt.state());
      delay(1500);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(800);

  Serial1.begin(115200, SERIAL_8N1, UART_RX, UART_TX);
  Serial.println("[UART] Serial1 ready on GPIO18/19");

  connectWiFi();
  connectMQTT();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (!mqtt.connected()) connectMQTT();
  mqtt.loop();
}
