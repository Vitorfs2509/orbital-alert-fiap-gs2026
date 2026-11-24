#!/usr/bin/env bash
set -euo pipefail
directory="${1:-ci-artifacts}"
mkdir -p "$directory"
directory="$(cd "$directory" && pwd)"
scanner="${TRIVY_IMAGE:-ghcr.io/aquasecurity/trivy@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969}"
project="${COMPOSE_PROJECT_NAME:-orbital-ci}"
result=0
for pair in "backend:$project-backend" "frontend:$project-frontend" "python:orbital-alert-tools:local" "postgres:postgres:16-bookworm"; do
  label="${pair%%:*}"
  image="${pair#*:}"
  if ! docker save "$image" -o "$directory/scan-image.tar"; then
    result=1
    continue
  fi
  if ! docker run --rm -v orbital-trivy-cache:/root/.cache/trivy -v "$directory:/out" "$scanner" image \
       --input /out/scan-image.tar --scanners vuln --severity HIGH,CRITICAL --exit-code 1 \
       --format json --output "/out/trivy-$label.json" > "$directory/trivy-$label.txt" 2>&1; then
    result=1
  fi
  rm -f -- "$directory/scan-image.tar"
done
exit "$result"
