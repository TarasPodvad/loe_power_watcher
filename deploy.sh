#!/usr/bin/env bash
# Azure setup + deploy (Flex Consumption, Python) using only Azure CLI.
# Safe to re-run: creates missing resources, updates settings, redeploys code.
# Needs: `az login` + `az account set --subscription ...`. First run also needs BOT_TOKEN / CHAT_IDS exported.
set -euo pipefail
cd "$(dirname "$0")"

RG=${RG:-rg-loe-watcher}
REGION=${REGION:-northeurope}            # check: az functionapp list-flexconsumption-locations -o table
APP=${APP:-loe-watcher-taras}            # globally unique
STORAGE=${STORAGE:-stloewatchertaras}    # globally unique, 3-24 lowercase letters/digits
GROUP_NAME=${GROUP_NAME:-Група 5.1.}

echo "Subscription: $(az account show --query name -o tsv)"

az group create -n "$RG" -l "$REGION" -o none

az storage account show -n "$STORAGE" -g "$RG" -o none 2>/dev/null || \
  az storage account create -n "$STORAGE" -g "$RG" -l "$REGION" --sku Standard_LRS \
    --allow-blob-public-access false --min-tls-version TLS1_2 -o none

az functionapp show -n "$APP" -g "$RG" -o none 2>/dev/null || \
  az functionapp create -g "$RG" -n "$APP" --storage-account "$STORAGE" \
    --flexconsumption-location "$REGION" --runtime python --runtime-version 3.11 -o none

# secrets only when provided -> code-only redeploys need no .env
if [[ -n "${BOT_TOKEN:-}" && -n "${CHAT_IDS:-}" ]]; then
  az functionapp config appsettings set -g "$RG" -n "$APP" -o none --settings \
    "BOT_TOKEN=$BOT_TOKEN" "CHAT_IDS=$CHAT_IDS" "GROUP_NAME=$GROUP_NAME"
elif ! az functionapp config appsettings list -g "$RG" -n "$APP" --query "[?name=='BOT_TOKEN'].name" -o tsv | grep -q BOT_TOKEN; then
  echo "First deploy: export BOT_TOKEN and CHAT_IDS"; exit 1
fi

# package = committed files only (never .env / local settings)
ZIP=$(mktemp -d)/app.zip
git archive --format=zip -o "$ZIP" HEAD
az functionapp deployment source config-zip -g "$RG" -n "$APP" --src "$ZIP" --build-remote true -o none

echo "Deployed $APP in $RG. Logs: Azure portal -> $APP -> Log stream (or Application Insights)."
