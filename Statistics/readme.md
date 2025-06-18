### DOPOLNITVE PROJEKTA

**docker-compose.yml**

- **Mosquitto MQTT Exporter**: Izvoz diagnostičnih podatkov iz Mosquitto MQTT
- **Prometheus**: Sistem za monitoring
- **Grafana**: Vizualizacija diagnostičnih podatkov

**Prometheus**
Datoteka data_prometheus/prometheus.yml definira vire zajemanja diagnostičnih podatkov

**Python**
producer.py ima dodatno mertiko, ki šteje število poslanih sporočil

## ZAGON SISTEMA
- docker compose up

Po zagonu python skripte **producer.py** preverimo naslov: http://localhost:8000

Prometheus potrebuje dostop do python metrike
- odpreti je potrebno port 8000

Preverimo ali **Prometheus** pravilno deluje: http://localhost:9090
V menuju izberimo Status/Targets - Exporter in python skripta morata imeti status UP.
V meniju izberemo Graph in z **metrics explorerjem** preverimo seznam metrik, ki so na voljo.

Nadaljujmo na **Grafano**: http://localhost:3000 (admin/admin)

Dodajmo novo povezavo:
- V meniju izberemo Connections/Add new connection
- Poiščemo Prometheus
- Add new data source - zgoraj levo
- V Prometheus server URL vnesemo: http://prometheus:9090
- Save & Test

Dodajmo nov Dashboard
- V meniju izberemo Dashboards
- Desno zgoraj New/Import
- Izberimo data_grafana/dashboard.json
- Nastavimo Prometheus datasource

## Dodatno
Docker metrics to Prometheus/Grafana
- https://docs.docker.com/config/daemon/prometheus/
