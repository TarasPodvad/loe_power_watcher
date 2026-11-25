#!/usr/bin/env bash
# One-time Azure setup + deploy (Flex Consumption, Python). Needs: az CLI, Azure Functions Core Tools (func), logged in via `az login`.
# Re-deploy code later with: func azure functionapp publish "$APP"
set -euo pipefail

RG=${RG:-rg-loe-watcher}
REGION=${REGION:-northeurope}          # check: az functionapp list-flexconsumption-locations -o table
APP=${APP:-loe-watcher-$RANDOM}        # must be globally unique
STORAGE=${STORAGE:-stloewatcher$RANDOM} # 3-24 lowercase letters/digits
: "${BOT_TOKEN:?export BOT_TOKEN first}"
: "${CHAT_IDS:?export CHAT_IDS first (comma-separated)}"
GROUP_NAME=${GROUP_NAME:-Група 5.1.}

az group create -n "$RG" -l "$REGION" -o none
az storage account create -n "$STORAGE" -g "$RG" -l "$REGION" --sku Standard_LRS --allow-blob-public-access false -o none
az functionapp create -g "$RG" -n "$APP" --storage-account "$STORAGE" \
  --flexconsumption-location "$REGION" --runtime python --runtime-version 3.11 -o none
az functionapp config appsettings set -g "$RG" -n "$APP" -o none --settings \
  "BOT_TOKEN=$BOT_TOKEN" "CHAT_IDS=$CHAT_IDS" "GROUP_NAME=$GROUP_NAME"

func azure functionapp publish "$APP"
echo "Deployed: $APP (RG $RG). Logs: az webapp log tail -g $RG -n $APP  or App Insights."
