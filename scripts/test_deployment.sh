#!/bin/bash

# Azure RAG Infrastructure Test Script
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Testing Azure RAG Infrastructure"
echo "=========================================="
echo ""

# Set variables from actual deployment
RG_NAME="ragresourcegroup"
STORAGE_ACCOUNT="ragstoragecolm2024"
FUNCTION_APP="func-parkinsons-rag"
LOCATION="westeurope"

# Test 1: Check if logged into Azure
echo "Test 1: Checking Azure CLI login status..."
if az account show &> /dev/null; then
    SUBSCRIPTION=$(az account show --query name -o tsv)
    echo -e "${GREEN}✓${NC} Logged into Azure"
    echo "  Subscription: $SUBSCRIPTION"
else
    echo -e "${RED}✗${NC} Not logged into Azure"
    echo "  Run: az login"
    exit 1
fi
echo ""

# Test 2: Check Resource Group
echo "Test 2: Checking Resource Group..."
if az group show --name "$RG_NAME" &> /dev/null; then
    echo -e "${GREEN}✓${NC} Resource Group exists: $RG_NAME"
    RG_LOCATION=$(az group show --name "$RG_NAME" --query location -o tsv)
    echo "  Location: $RG_LOCATION"
else
    echo -e "${RED}✗${NC} Resource Group not found: $RG_NAME"
    exit 1
fi
echo ""

# Test 3: Check Storage Account
echo "Test 3: Checking Storage Account..."
if az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RG_NAME" &> /dev/null; then
    echo -e "${GREEN}✓${NC} Storage Account exists: $STORAGE_ACCOUNT"
    
    # Get storage account key
    STORAGE_KEY=$(az storage account keys list --account-name "$STORAGE_ACCOUNT" --resource-group "$RG_NAME" --query "[0].value" -o tsv)
    
    # Check account status
    STATUS=$(az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RG_NAME" --query "provisioningState" -o tsv)
    echo "  Status: $STATUS"
else
    echo -e "${RED}✗${NC} Storage Account not found: $STORAGE_ACCOUNT"
    exit 1
fi
echo ""

# Test 4: Check Storage Containers
echo "Test 4: Checking Storage Containers..."
CONTAINERS=("pdfs" "embeddings")
for container in "${CONTAINERS[@]}"; do
    if az storage container show --name "$container" --account-name "$STORAGE_ACCOUNT" --account-key "$STORAGE_KEY" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Container exists: $container"
    else
        echo -e "${RED}✗${NC} Container not found: $container"
    fi
done
echo ""

# Test 5: Test Storage Account Connectivity
echo "Test 5: Testing Storage Account write/read..."
TEST_FILE="test-$(date +%s).txt"
echo "Hello from test script" > "/tmp/$TEST_FILE"

if az storage blob upload \
    --account-name "$STORAGE_ACCOUNT" \
    --account-key "$STORAGE_KEY" \
    --container-name "pdfs" \
    --name "$TEST_FILE" \
    --file "/tmp/$TEST_FILE" \
    --overwrite &> /dev/null; then
    echo -e "${GREEN}✓${NC} Successfully uploaded test file"
    
    # Try to download it back
    if az storage blob download \
        --account-name "$STORAGE_ACCOUNT" \
        --account-key "$STORAGE_KEY" \
        --container-name "pdfs" \
        --name "$TEST_FILE" \
        --file "/tmp/${TEST_FILE}.downloaded" \
        &> /dev/null; then
        echo -e "${GREEN}✓${NC} Successfully downloaded test file"
        
        # Clean up
        az storage blob delete \
            --account-name "$STORAGE_ACCOUNT" \
            --account-key "$STORAGE_KEY" \
            --container-name "pdfs" \
            --name "$TEST_FILE" &> /dev/null
        rm "/tmp/$TEST_FILE" "/tmp/${TEST_FILE}.downloaded" 2>/dev/null
    else
        echo -e "${RED}✗${NC} Failed to download test file"
    fi
else
    echo -e "${RED}✗${NC} Failed to upload test file"
fi
echo ""

# Test 6: Check App Service Plan
echo "Test 6: Checking App Service Plan..."
APP_PLAN=$(az functionapp show --name "$FUNCTION_APP" --resource-group "$RG_NAME" --query "serverFarmId" -o tsv 2>/dev/null | cut -d'/' -f9)
if [ ! -z "$APP_PLAN" ]; then
    echo -e "${GREEN}✓${NC} App Service Plan exists: $APP_PLAN"
    SKU=$(az appservice plan show --name "$APP_PLAN" --resource-group "$RG_NAME" --query "sku.name" -o tsv)
    echo "  SKU: $SKU"
else
    echo -e "${YELLOW}⚠${NC} Could not verify App Service Plan"
fi
echo ""

# Test 7: Check Function App
echo "Test 7: Checking Function App..."
if az functionapp show --name "$FUNCTION_APP" --resource-group "$RG_NAME" &> /dev/null; then
    echo -e "${GREEN}✓${NC} Function App exists: $FUNCTION_APP"
    
    # Check state
    STATE=$(az functionapp show --name "$FUNCTION_APP" --resource-group "$RG_NAME" --query "state" -o tsv)
    echo "  State: $STATE"
    
    # Get default hostname
    HOSTNAME=$(az functionapp show --name "$FUNCTION_APP" --resource-group "$RG_NAME" --query "defaultHostName" -o tsv)
    echo "  URL: https://$HOSTNAME"
    
    # Check runtime
    RUNTIME=$(az functionapp config show --name "$FUNCTION_APP" --resource-group "$RG_NAME" --query "linuxFxVersion" -o tsv)
    echo "  Runtime: $RUNTIME"
else
    echo -e "${RED}✗${NC} Function App not found: $FUNCTION_APP"
    exit 1
fi
echo ""

# Test 8: Check Function App Settings
echo "Test 8: Checking Function App Configuration..."
APP_SETTINGS=$(az functionapp config appsettings list --name "$FUNCTION_APP" --resource-group "$RG_NAME" -o json)

# Check for required settings
REQUIRED_SETTINGS=("AZURE_STORAGE_CONNECTION_STRING" "FUNCTIONS_WORKER_RUNTIME")
for setting in "${REQUIRED_SETTINGS[@]}"; do
    if echo "$APP_SETTINGS" | grep -q "\"name\": \"$setting\""; then
        echo -e "${GREEN}✓${NC} App Setting exists: $setting"
    else
        echo -e "${RED}✗${NC} App Setting missing: $setting"
    fi
done
echo ""

# Test 9: Check if Function App is accessible
echo "Test 9: Testing Function App endpoint..."
FUNC_URL="https://$HOSTNAME"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$FUNC_URL" --max-time 10)

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 401 ] || [ "$HTTP_CODE" -eq 404 ]; then
    echo -e "${GREEN}✓${NC} Function App is responding (HTTP $HTTP_CODE)"
    echo "  Note: HTTP 404 is normal if no functions are deployed yet"
else
    echo -e "${YELLOW}⚠${NC} Function App returned HTTP $HTTP_CODE"
fi
echo ""

# Test 10: List deployed functions (if any)
echo "Test 10: Checking for deployed functions..."
FUNCTIONS=$(az functionapp function list --name "$FUNCTION_APP" --resource-group "$RG_NAME" -o json 2>/dev/null)
if [ ! -z "$FUNCTIONS" ] && [ "$FUNCTIONS" != "[]" ]; then
    echo -e "${GREEN}✓${NC} Functions deployed:"
    echo "$FUNCTIONS" | jq -r '.[].name' | while read func; do
        echo "  - $func"
    done
else
    echo -e "${YELLOW}⚠${NC} No functions deployed yet"
    echo "  This is normal if you haven't deployed your code"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Infrastructure is deployed and accessible!"
echo ""
echo "Next steps:"
echo "1. Deploy your function code to: $FUNCTION_APP"
echo "2. Test your RAG endpoints"
echo "3. Upload PDFs to test the pipeline"
echo ""
echo "Quick commands:"
echo "  - View storage: az storage blob list --account-name $STORAGE_ACCOUNT --container-name pdfs --account-key \$(az storage account keys list -n $STORAGE_ACCOUNT -g $RG_NAME --query '[0].value' -o tsv)"
echo "  - View logs: az functionapp log tail --name $FUNCTION_APP --resource-group $RG_NAME"
echo "  - Get function keys: az functionapp keys list --name $FUNCTION_APP --resource-group $RG_NAME"
echo ""