# Monitor funcional de API con Python

Objetivo y arquitectura

Detectar respuestas HTTP exitosas que contienen datos incompletos. La API simulada declara 150 registros funcional y puede entregar 120 para reproducir el fallo. El monitor valida el contrato JSON, publica métricas y genera trazas. Prometheus recopila métricas y Grafana las visualiza.

API Python	http://localhost:8080/api/consultar
Monitor Python	http://localhost:8000/metrics
Prometheus	http://localhost:9090
Grafana	http://localhost:3000
Collector OTLP	http://localhost:4318/v1/traces


## Inicio

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
```

En otra terminal, configure la URL y un umbral adecuado para un endpoint de prueba **sin datos personales**:

```bash
# Linux/macOS
export CHECK_URL=http://localhost:8080/api/consultar
export CHECK_METHOD=GET
export EXPECTED_MIN_RECORDS=1
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
python monitor.py
```

En PowerShell use `$env:CHECK_URL='...'` y análogamente las otras variables. Si el endpoint usa POST, defina `CHECK_METHOD=POST` y `CHECK_JSON_BODY` con el JSON de consulta.

- Métricas: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (configure Prometheus como datasource: `http://prometheus:9090`)
- El Collector registra las trazas recibidas en sus logs: `docker compose logs -f otel-collector`.

## Consultas PromQL

```promql
app_functional_ok == 0
sum(increase(app_synthetic_checks_total{outcome="failure"}[5m]))
app_records_returned
histogram_quantile(0.95, sum by (le) (rate(app_check_duration_seconds_bucket[5m])))
```

