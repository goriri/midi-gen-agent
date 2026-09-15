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
echo "==> [1/4] Enabling Google Cloud Services..."
gcloud services enable \
  compute.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  storage.googleapis.com \
  firestore.googleapis.com \
  orgpolicy.googleapis.com \
  --project="${PROJECT_ID}"

# Ensure Cloud Run unauthenticated access is permitted by Org Policy (if applicable)
cat <<EOF > /tmp/allow_all_domains_${PROJECT_ID}.yaml
name: projects/${PROJECT_ID}/policies/iam.allowedPolicyMemberDomains
spec:
  rules:
  - allowAll: true
EOF
gcloud org-policies set-policy "/tmp/allow_all_domains_${PROJECT_ID}.yaml" --project="${PROJECT_ID}" --quiet >/dev/null 2>&1 || true
rm -f "/tmp/allow_all_domains_${PROJECT_ID}.yaml"

# Grant required IAM roles to Default Compute Service Account (needed for Cloud Run source build & runtime Vertex AI/GCS access on new projects)
echo "==> [2/4] Configuring IAM roles for default service account..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
for ROLE in \
  "roles/storage.admin" \
  "roles/aiplatform.user" \
  "roles/datastore.user" \
  "roles/logging.logWriter" \
  "roles/artifactregistry.writer" \
  "roles/cloudbuild.builds.builder"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="${ROLE}" \
    --condition=None \
    --quiet >/dev/null 2>&1 || true
done

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
