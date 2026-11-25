import json
import logging
import os
import time
from urllib.parse import urlparse

import requests
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
URL = os.getenv('CHECK_URL', 'http://localhost:8080/api/consultar')
METHOD = os.getenv('CHECK_METHOD', 'GET').upper()
INTERVAL = max(5, int(os.getenv('CHECK_INTERVAL_SECONDS', '60')))
EXPECTED_MIN = int(os.getenv('EXPECTED_MIN_RECORDS', '1'))
METRICS_PORT = int(os.getenv('METRICS_PORT', '8000'))
BODY = os.getenv('CHECK_JSON_BODY')

checks = Counter('app_synthetic_checks_total', 'Synthetic checks', ['outcome'])
functional_ok = Gauge('app_functional_ok', 'Whether the last check passed (1/0)')
records = Gauge('app_records_returned', 'Number of returned records')
latency = Histogram('app_check_duration_seconds', 'Synthetic check latency', buckets=(.1,.25,.5,1,2,5,10,20))

provider = TracerProvider(resource=Resource.create({'service.name': 'python-synthetic-monitor'}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer('synthetic-monitor')

def run_check():
    start = time.monotonic()
    outcome = 'failure'
    count = 0
    try:
        with tracer.start_as_current_span('check_api_integrity') as span:
            span.set_attribute('http.request.method', METHOD)
            span.set_attribute('server.address', urlparse(URL).hostname or 'unknown')
            kwargs = {'timeout': 10}
            if BODY is not None:
                kwargs['json'] = json.loads(BODY)
            response = requests.request(METHOD, URL, **kwargs)
            span.set_attribute('http.response.status_code', response.status_code)
            response.raise_for_status()
            payload = response.json()
            # Contract: {"status": 200, "data": [...], "totalRegistros": N}
            if not isinstance(payload, dict) or payload.get('status') != 200:
                raise ValueError('Invalid application status')
            data = payload.get('data')
            if not isinstance(data, list):
                raise ValueError('data is not a list')
            count = len(data)
            if count < EXPECTED_MIN:
                raise ValueError(f'Only {count} records; minimum {EXPECTED_MIN}')
            total = payload.get('totalRegistros')
            if total is not None and int(total) != count:
                raise ValueError(f'Count mismatch: totalRegistros={total}, data={count}')
            outcome = 'success'
    except Exception as exc:
        logging.warning('Functional check failed: %s', exc)
    finally:
        duration = time.monotonic() - start
        latency.observe(duration)
        records.set(count)
        functional_ok.set(1 if outcome == 'success' else 0)
        checks.labels(outcome=outcome).inc()
        logging.info('outcome=%s records=%s duration=%.3fs', outcome, count, duration)

if __name__ == '__main__':
    start_http_server(METRICS_PORT)
    logging.info('Metrics exposed on :%d/metrics', METRICS_PORT)
    while True:
        run_check()
        time.sleep(INTERVAL)
