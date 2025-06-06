import pandas as pd
import json
import time
import paho.mqtt.client as mqtt
from prometheus_client import Counter, start_http_server

# === Prometheus metrike ===
sent_messages = Counter('sent_predictions_total', 'Skupno št. poslanih sporočil')
status_counter = Counter('fatigue_status_total', 'Število po statusih utrujenosti', ['status'])

# === Branje CSV ===
df = pd.read_csv('fatigue_predictions.csv')
df.columns = df.columns.str.strip()  # 🔧 odstrani presledke okoli imen stolpcev

# === MQTT nastavitve ===
broker = "127.0.0.1"
port = 1883
topic = "/fatigue"

client = mqtt.Client(client_id="csv_producer", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect(broker, port, 60)

# === Prometheus strežnik ===
start_http_server(8000)

# === Pošiljanje po vrsticah ===
for index, row in df.iterrows():
    try:
        status = row['label'].strip()  # odstrani presledke, če obstajajo

        message = {
            "status": status
        }

        # Pošlji sporočilo v MQTT
        client.publish(topic, json.dumps(message))
        print(f"Poslano: {message}")

        # Posodobi Prometheus metrike
        sent_messages.inc()
        status_counter.labels(status=status).inc()

        time.sleep(2)

    except KeyError as e:
        print(f"Napaka: stolpec {e} ne obstaja.")
        break
    except Exception as e:
        print(f"Napaka pri pošiljanju: {e}")
        break
