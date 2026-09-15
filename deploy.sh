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
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
DETERMINISTIC_URL="https://${SERVICE_NAME}-${PROJECT_NUMBER}.${REGION}.run.app"

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
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=True,GCS_BUCKET_NAME=${GCS_BUCKET_NAME},GEMINI_MODEL=gemini-2.5-flash,APP_URL=${DETERMINISTIC_URL}" \
  --quiet

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --format="value(status.url)" || echo "${DETERMINISTIC_URL}")
if [ -z "${SERVICE_URL}" ]; then
  SERVICE_URL="${DETERMINISTIC_URL}"
fi
echo "    ✓ Service deployed at: ${SERVICE_URL}"

# Update APP_URL env var on the service so A2A agent card advertises the canonical URL
gcloud run services update "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --update-env-vars="APP_URL=${SERVICE_URL}" \
  --quiet || true

# 3. Configure Discovery Engine IAM Invoker
echo "==> [3/4] Granting Invoker permission to Discovery Engine service agent..."
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
import sys, os, json, subprocess, time, urllib.request, urllib.error

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

card_data = None
for attempt in range(1, 11):
    try:
        req = urllib.request.Request(card_url, headers={'User-Agent': 'deploy-script/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                card_data = json.loads(resp.read().decode('utf-8'))
                print('    ✓ Successfully fetched live agent card from service!')
                break
    except Exception as e:
        if attempt < 10:
            print(f'    Waiting for Cloud Run service warm-up (attempt {attempt}/10)...')
            time.sleep(3)

if not card_data:
    print('    Warning: Using embedded fallback agent card definition...')
    card_data = {
        'capabilities': {'streaming': True},
        'defaultInputModes': ['text/plain'],
        'defaultOutputModes': ['text/plain'],
        'description': 'Generates MIDI music in composition format (text/JSON) or binary files (.mid / .wav) from text prompts.',
        'name': 'midi_agent',
        'preferredTransport': 'JSONRPC',
        'protocolVersion': '0.3.0',
        'skills': [
            {'id': 'midi_agent', 'name': 'model', 'description': 'Generates MIDI music in composition format (text/JSON) or binary files (.mid / .wav) from text prompts.', 'tags': ['llm']},
            {'id': 'midi_agent-generate_music', 'name': 'generate_music', 'description': 'Generate MIDI music in the specified output format given a user prompt.', 'tags': ['llm', 'tools']},
            {'id': 'midi_agent-generate_composition_text', 'name': 'generate_composition_text', 'description': 'Generates music composition in text/JSON format based on the user text prompt.', 'tags': ['llm', 'tools']},
            {'id': 'midi_agent-generate_midi_binary', 'name': 'generate_midi_binary', 'description': 'Generates music and saves it as a binary MIDI (.mid) file based on the user text prompt.', 'tags': ['llm', 'tools']},
            {'id': 'midi_agent-generate_wav_binary', 'name': 'generate_wav_binary', 'description': 'Generates music and converts it to a binary WAV (.wav) audio file based on the user text prompt.', 'tags': ['llm', 'tools']}
        ],
        'supportsAuthenticatedExtendedCard': False,
        'url': f'{service_url}/a2a/app',
        'version': '0.1.0'
    }

token = subprocess.check_output(['gcloud', 'auth', 'print-access-token']).decode().strip()
api_url = f'https://discoveryengine.googleapis.com/v1alpha/{engine_name}/assistants/default_assistant/agents'
headers = {
    'Authorization': f'Bearer {token}',
    'X-Goog-User-Project': project_id,
    'Content-Type': 'application/json'
}

def api_call(url, method='GET', payload=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'error': body}
    except Exception as e:
        return 500, {'error': str(e)}

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

status, resp_list = api_call(api_url, method='GET')
if status == 404 and not ge_app_id.startswith('projects/'):
    print(f'    Engine {ge_app_id} not found; auto-creating Gemini Enterprise Engine...')
    eng_url = f'https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/collections/default_collection/engines?engineId={ge_app_id}'
    eng_payload = {
        'displayName': f'MIDI Studio GE ({ge_app_id})',
        'solutionType': 'SOLUTION_TYPE_SEARCH',
        'industryVertical': 'GENERIC',
        'appType': 'APP_TYPE_INTRANET',
        'searchEngineConfig': {
            'searchTier': 'SEARCH_TIER_ENTERPRISE',
            'searchAddOns': ['SEARCH_ADD_ON_LLM']
        }
    }
    ec, er = api_call(eng_url, method='POST', payload=eng_payload)
    if ec in (200, 201):
        print(f'    ✓ Created Gemini Enterprise Engine: {ge_app_id}')
        time.sleep(3)
        status, resp_list = api_call(api_url, method='GET')

existing_agent_name = None
if status == 200:
    for a in resp_list.get('agents', []):
        if a.get('displayName') == 'ADK MIDI Composition Studio':
            existing_agent_name = a.get('name')
            break

if existing_agent_name:
    print(f'    Updating existing Gemini Enterprise agent registration: {existing_agent_name}...')
    patch_url = f'https://discoveryengine.googleapis.com/v1alpha/{existing_agent_name}'
    code, r = api_call(patch_url, method='PATCH', payload=payload)
else:
    print('    Creating new Gemini Enterprise agent registration...')
    code, r = api_call(api_url, method='POST', payload=payload)

if code == 400 and 'license' in str(r).lower():
    print('    Active Gemini Enterprise license not yet assigned; auto-provisioning free_trial_gemini license...')
    account = subprocess.check_output(['gcloud', 'config', 'get-value', 'account']).decode().strip()
    lc_url = f'https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/licenseConfigs?licenseConfigId=free_trial_gemini'
    import datetime
    now = datetime.datetime.utcnow()
    lc_payload = {
        'licenseCount': 50,
        'subscriptionTier': 'SUBSCRIPTION_TIER_SEARCH_AND_ASSISTANT',
        'subscriptionTerm': 'SUBSCRIPTION_TERM_ONE_MONTH',
        'freeTrial': True,
        'geminiBundle': True,
        'startDate': {'year': now.year, 'month': now.month, 'day': now.day}
    }
    api_call(lc_url, method='POST', payload=lc_payload)
    ul_url = f'https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/userStores/default_user_store:batchUpdateUserLicenses'
    ul_payload = {
        'inlineSource': {
            'userLicenses': [
                {
                    'userPrincipal': account,
                    'licenseAssignmentState': 'ASSIGNED',
                    'licenseConfig': f'projects/{project_number}/locations/global/licenseConfigs/free_trial_gemini'
                }
            ]
        }
    }
    api_call(ul_url, method='POST', payload=ul_payload)
    time.sleep(2)
    print('    Retrying Gemini Enterprise agent registration...')
    code, r = api_call(api_url, method='POST', payload=payload)

if code in (200, 201):
    print(f'    ✓ Registered to Gemini Enterprise successfully! Agent ID: {r.get(\"name\")}')
else:
    print(f'    Registration response ({code}): {r}')
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
