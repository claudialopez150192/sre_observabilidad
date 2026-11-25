# Monitor funcional de API con Python

## 1. Objetivo y arquitectura

Detectar respuestas HTTP exitosas que contienen datos incompletos o inconsistentes, incluso cuando la infraestructura se encuentra operativa.

La API simulada declara 150 registros, pero puede devolver únicamente 120 para reproducir un fallo silencioso.

El monitor desarrollado en Python valida el contrato JSON, publica métricas personalizadas y genera trazas mediante OpenTelemetry. Prometheus recopila las métricas y Grafana permite visualizar los resultados.

## 2. Componentes y servicios locales

| Componente | URL |
|---|---|
| API Python | [http://localhost:8080/api/consultar](http://localhost:8080/api/consultar) |
| Monitor Python | [http://localhost:8000/metrics](http://localhost:8000/metrics) |
| Prometheus | [http://localhost:9090](http://localhost:9090) |
| Grafana | [http://localhost:3000](http://localhost:3000) |
| OpenTelemetry Collector (OTLP) | `http://localhost:4318/v1/traces` |

## 3. Documentación técnica

Para obtener información detallada sobre la instalación, configuración, ejecución local, métricas personalizadas, dashboards y pruebas funcionales, consultar el siguiente manual:

**[Consultar manual técnico de ejecución local (PDF)](docs/manual_ejecucion_local_sre.pdf)**