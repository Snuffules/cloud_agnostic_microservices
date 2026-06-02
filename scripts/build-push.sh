#!/usr/bin/env bash
set -euo pipefail

CLOUD="${1:?Usage: ./scripts/build-push.sh <gcp|aws|azure> <service>}"
SERVICE="${2:?Usage: ./scripts/build-push.sh <gcp|aws|azure> <service>}"
TAG="${TAG:-v1.0.0}"

case "$CLOUD" in
  gcp)
    PROJECT_ID="${PROJECT_ID:?PROJECT_ID is required for GCP}"
    GCP_ARTIFACT_REGISTRY_LOCATION="${GCP_ARTIFACT_REGISTRY_LOCATION:-europe-west1}"
    IMAGE="${GCP_ARTIFACT_REGISTRY_LOCATION}-docker.pkg.dev/${PROJECT_ID}/apps/${SERVICE}:${TAG}"
    ;;
  aws)
    ACCOUNT_ID="${ACCOUNT_ID:?ACCOUNT_ID is required for AWS}"
    REGION="${REGION:?REGION is required for AWS}"
    IMAGE="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${SERVICE}:${TAG}"
    ;;
  azure)
    ACR_NAME="${ACR_NAME:?ACR_NAME is required for Azure}"
    IMAGE="${ACR_NAME}.azurecr.io/${SERVICE}:${TAG}"
    ;;
  *)
    echo "Unsupported cloud: ${CLOUD}" >&2
    exit 1
    ;;
esac

echo "Building ${IMAGE}"
docker build -t "${IMAGE}" "./apps/${SERVICE}"

echo "Pushing ${IMAGE}"
docker push "${IMAGE}"
