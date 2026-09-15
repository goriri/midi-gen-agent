#!/bin/bash
# ==============================================================================
# setup.sh — Resource Setup for ADK MIDI Composition Studio
# Creates required GCP resources (Storage Bucket, Firestore, enables APIs)
# ==============================================================================

set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${REGION:-us-central1}"

if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
fi

if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID is required."
  echo "Usage: ./setup.sh <PROJECT_ID> [REGION]"
  exit 1
fi

echo "=================================================="
echo " Setting up resources for ADK MIDI Agent"
echo " Project: ${PROJECT_ID}"
echo " Region:  ${REGION}"
echo "=================================================="

# 1. Enable Required Services
echo "==> [1/3] Enabling Google Cloud Services..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  storage.googleapis.com \
  firestore.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Cloud Storage Bucket for MIDI and WAV files
GCS_BUCKET_NAME="${PROJECT_ID}-midi-studio"
echo "==> [2/3] Checking Cloud Storage Bucket: gs://${GCS_BUCKET_NAME}..."
if ! gcloud storage buckets describe "gs://${GCS_BUCKET_NAME}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "    Creating bucket gs://${GCS_BUCKET_NAME} in ${REGION}..."
  gcloud storage buckets create "gs://${GCS_BUCKET_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --uniform-bucket-level-access || true
else
  echo "    Bucket gs://${GCS_BUCKET_NAME} already exists."
fi

# 3. Firestore Database for Generation History
echo "==> [3/3] Checking Firestore Database..."
if ! gcloud firestore databases describe --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "    Creating Firestore (default) database in ${REGION}..."
  gcloud firestore databases create \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --type=firestore-native || true
else
  echo "    Firestore database already exists."
fi

echo "=================================================="
echo " Setup complete! Next: run ./deploy.sh ${PROJECT_ID}"
echo "=================================================="
