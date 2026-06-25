# dockerized-app-cicd

A containerized web app with a **complete CI/CD pipeline** — lint, test, container scan, push to
GitHub Container Registry with **keyless cosign signing**, and a deploy step. The app runs on a
**production WSGI server (gunicorn)** and exposes **Prometheus metrics**. The reference
implementation for the "DevOps My App" learning project.

## Stack

- **App:** Flask service with `/health` and a Prometheus `/metrics` endpoint
- **Server:** gunicorn (production WSGI) — not the Flask dev server
- **Container:** slim base image, runs as non-root, build-time version stamp, healthcheck
- **CI/CD:** GitHub Actions — lint → test → build → Trivy scan → push to GHCR → cosign sign → deploy
- **Observability:** Prometheus metrics (request count + latency histogram)

## Pipeline

```
lint (ruff) → test (pytest) → docker build → Trivy scan → push GHCR → cosign sign → deploy
```

## Run locally

```bash
pip install -r requirements.txt
python app.py                      # dev server, http://localhost:8080

# or production-style with gunicorn:
gunicorn --bind 0.0.0.0:8080 app:app

# or with Docker:
docker build -t dockerized-app-cicd .
docker run -p 8080:8080 dockerized-app-cicd

# or with compose:
docker compose up --build
```

## Endpoints

| Path | Purpose |
|------|---------|
| `/` | App index (JSON, includes version) |
| `/health` | Liveness/uptime check (used by monitoring) |
| `/metrics` | Prometheus metrics (request count + latency) |

## Observability

The `/metrics` endpoint exposes:

- `http_requests_total{method,endpoint,status}` — request counter
- `http_request_duration_seconds{method,endpoint}` — latency histogram

Point a Prometheus scrape at `/metrics`, or pair this with the
[prometheus-grafana-docker](https://github.com/durrello/prometheus-grafana-docker) stack for
dashboards and alerts.

## Monitoring (uptime)

Point [UptimeRobot](https://uptimerobot.com/) or Healthchecks at `https://<your-host>/health` with a
5-minute interval and email/Slack alerts. The endpoint returns `200 {"status":"ok"}`.

## What this demonstrates

- A real, green CI/CD pipeline (not a toy) with tests and a security gate
- **Supply-chain security:** keyless image signing with cosign via GitHub OIDC (no stored keys)
- Container best practices: non-root user, healthcheck, slim base image, version stamping
- Production serving with gunicorn instead of the Flask dev server
- Built-in Prometheus metrics for observability

## License

MIT
