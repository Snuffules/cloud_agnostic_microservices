#!/usr/bin/env bash
set -euo pipefail

CLOUD="${1:?Usage: ./scripts/deploy-service.sh <gcp|aws|azure> <service>}"
SERVICE="${2:?Usage: ./scripts/deploy-service.sh <gcp|aws|azure> <service>}"

case "$CLOUD" in
  gcp|aws|azure) ;;
  *)
    echo "Unsupported cloud: ${CLOUD}" >&2
    exit 1
    ;;
esac

kubectl apply -k k8s/platform
kubectl apply -k "k8s/services/${SERVICE}/overlays/${CLOUD}"
