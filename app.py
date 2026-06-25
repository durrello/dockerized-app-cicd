import os
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "dev")

# Prometheus metrics.
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


@app.before_request
def _start_timer():
    request._start_time = time.perf_counter()


@app.after_request
def _record_metrics(response):
    # Skip the metrics endpoint itself to avoid self-referential noise.
    endpoint = request.path
    if endpoint != "/metrics":
        latency = time.perf_counter() - getattr(request, "_start_time", time.perf_counter())
        REQUEST_LATENCY.labels(request.method, endpoint).observe(latency)
        REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
    return response


@app.get("/")
def index():
    return jsonify(
        app="dockerized-app-cicd",
        message="Containerized app with a full CI/CD pipeline",
        version=APP_VERSION,
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    # Dev server only — production runs via gunicorn (see Dockerfile).
    app.run(host="0.0.0.0", port=8080)
