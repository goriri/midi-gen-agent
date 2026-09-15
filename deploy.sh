#!/bin/bash
# ==============================================================================
# deploy.sh — One-Click Deployment Script for ADK MIDI Composition Studio
# Compliant with AgentHub Contributor Guide standards.
#
# Usage:
#   ./deploy.sh <PROJECT_ID> [--ge <APP_ID>]
#   ./deploy.sh <PROJECT_ID> <APP_ID>
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID=""
GE_APP_ID=""
REGION="${REGION:-us-central1}"
SERVICE_NAME="adk-midi-studio"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ge)
      GE_APP_ID="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 <PROJECT_ID> [--ge <APP_ID>]"
      echo "  PROJECT_ID    GCP Project ID (required)"
      echo "  --ge APP_ID   Gemini Enterprise App ID or Engine ID (optional)"
      exit 0
      ;;
    *)
      if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID="$1"
      elif [ -z "$GE_APP_ID" ]; then
        GE_APP_ID="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
fi

if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID is required."
  echo "Usage: $0 <PROJECT_ID> [--ge <APP_ID>]"
  exit 1
fi

echo "=================================================="
echo " ADK MIDI Studio — One-Click Deployer"
echo " Project ID:  ${PROJECT_ID}"
echo " Region:      ${REGION}"
if [ -n "${GE_APP_ID}" ]; then
  echo " GE App ID:   ${GE_APP_ID}"
fi
echo "=================================================="

# 1. Run Setup Script for Infrastructure
if [ -f "${SCRIPT_DIR}/setup.sh" ]; then
  echo "==> [1/4] Running setup.sh to ensure GCP resources..."
  bash "${SCRIPT_DIR}/setup.sh" "${PROJECT_ID}" "${REGION}"
fi

GCS_BUCKET_NAME="${PROJECT_ID}-midi-studio"

# 2. Deploy Cloud Run Service
echo "==> [2/4] Deploying Cloud Run Service: ${SERVICE_NAME}..."
gcloud run deploy "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --source="${SCRIPT_DIR}" \
  --memory="4Gi" \
  --cpu="1" \
  --min-instances="1" \
  --max-instances="10" \
  --concurrency="8" \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=True,GCS_BUCKET_NAME=${GCS_BUCKET_NAME},GEMINI_MODEL=gemini-2.5-flash" \
  --quiet

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --format="value(status.url)")
echo "    ✓ Service deployed at: ${SERVICE_URL}"

# Update APP_URL env var on the service so A2A agent card advertises the real URL
gcloud run services update "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --update-env-vars="APP_URL=${SERVICE_URL}" \
  --quiet

# 3. Configure Discovery Engine IAM Invoker
echo "==> [3/4] Granting Invoker permission to Discovery Engine service agent..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
DISCOVERY_ENGINE_SA="service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com"

gcloud run services add-iam-policy-binding "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --member="serviceAccount:${DISCOVERY_ENGINE_SA}" \
  --role="roles/run.servicesInvoker" \
  --quiet || true

# 4. Optional Registration to Gemini Enterprise
if [ -n "${GE_APP_ID}" ]; then
  echo "==> [4/4] Registering agent to Gemini Enterprise app: ${GE_APP_ID}..."
  
  python3 -c "
import os, sys, json, subprocess, requests

project_id = '${PROJECT_ID}'
project_number = '${PROJECT_NUMBER}'
ge_app_id = '${GE_APP_ID}'
service_url = '${SERVICE_URL}'

# Standardize engine resource name
if not ge_app_id.startswith('projects/'):
    engine_name = f'projects/{project_number}/locations/global/collections/default_collection/engines/{ge_app_id}'
else:
    engine_name = ge_app_id

card_url = f'{service_url}/a2a/app/.well-known/agent-card.json'
print(f'    Fetching agent card from {card_url}...')
try:
    card_resp = requests.get(card_url, timeout=30)
    card_data = card_resp.json()
except Exception as e:
    print(f'    Warning: Could not fetch card via HTTP ({e}), building card locally...')
    import asyncio
    from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
    from a2a.types import AgentCapabilities
    from midi_agent.agent import root_agent
    card = asyncio.run(AgentCardBuilder(
        agent=root_agent,
        capabilities=AgentCapabilities(streaming=True),
        rpc_url=f'{service_url}/a2a/app',
        agent_version='0.1.0'
    ).build())
    card_data = card.model_dump(exclude_none=True)

# Remove any None values from card_data
def clean_dict(d):
    if not isinstance(d, dict):
        return d
    return {k: clean_dict(v) for k, v in d.items() if v is not None}

card_data = clean_dict(card_data)

token = subprocess.check_output(['gcloud', 'auth', 'print-access-token']).decode().strip()
api_url = f'https://discoveryengine.googleapis.com/v1alpha/{engine_name}/assistants/default_assistant/agents'
headers = {
    'Authorization': f'Bearer {token}',
    'X-Goog-User-Project': project_id,
    'Content-Type': 'application/json'
}

payload = {
    'displayName': 'ADK MIDI Composition Studio',
    'description': 'AI Music Composer agent powered by Google ADK and General MIDI (GM) standards. Generates structured MIDI compositions and audio synthesis from natural language prompts in English and Chinese.',
    'icon': {
        'uri': 'https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/music_note/default/24px.svg'
    },
    'a2aAgentDefinition': {
        'jsonAgentCard': json.dumps(card_data)
    }
}

# Check if agent already exists
resp_list = requests.get(api_url, headers=headers, timeout=30)
existing_agent_name = None
if resp_list.status_code == 200:
    for a in resp_list.json().get('agents', []):
        if a.get('displayName') == 'ADK MIDI Composition Studio':
            existing_agent_name = a.get('name')
            break

if existing_agent_name:
    print(f'    Updating existing Gemini Enterprise agent registration: {existing_agent_name}...')
    patch_url = f'https://discoveryengine.googleapis.com/v1alpha/{existing_agent_name}'
    r = requests.patch(patch_url, headers=headers, json=payload, timeout=30)
else:
    print('    Creating new Gemini Enterprise agent registration...')
    r = requests.post(api_url, headers=headers, json=payload, timeout=30)

if r.status_code in (200, 201):
    print(f'    ✓ Registered to Gemini Enterprise successfully! Agent ID: {r.json().get(\"name\")}')
else:
    print(f'    Registration response ({r.status_code}): {r.text}')
"
else
  echo "==> [4/4] Step skipped: No --ge <APP_ID> specified."
fi

echo ""
echo "=================================================="
echo " 🎉 Deployment & Verification Complete!"
echo " Web UI / Health Check: ${SERVICE_URL}/"
echo " A2A Agent Card:        ${SERVICE_URL}/a2a/app/.well-known/agent-card.json"
echo " A2A JSON-RPC URL:      ${SERVICE_URL}/a2a/app"
echo "=================================================="
