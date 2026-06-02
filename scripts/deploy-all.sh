#!/usr/bin/env bash
set -euo pipefail

CLOUD="${1:?Usage: ./scripts/deploy-all.sh <gcp|aws|azure>}"

case "$CLOUD" in
  gcp|aws|azure) ;;
  *)
    echo "Unsupported cloud: ${CLOUD}" >&2
    exit 1
    ;;
esac

kubectl apply -k k8s/platform

while IFS= read -r SERVICE; do
  [[ -z "$SERVICE" || "$SERVICE" =~ ^# ]] && continue
  echo "Deploying ${SERVICE} to ${CLOUD}"
  kubectl apply -k "k8s/services/${SERVICE}/overlays/${CLOUD}"
done < services.txt
