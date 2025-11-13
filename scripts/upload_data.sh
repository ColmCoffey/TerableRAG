#!/bin/bash
# upload_data.sh
# Uploads embeddings (pickle files) and PDFs to Azure Blob Storage
# Run this when: Initial setup or when adding new papers/embeddings

set -e  # Exit immediately if a command exits with a non-zero status

echo "======================================"
echo "Uploading Data to Azure Storage"
echo "======================================"

# Check if Terraform has been run
if ! terraform output storage_account_name > /dev/null 2>&1; then
    echo "ERROR: Terraform outputs not found."
    echo "Run ./deploy_infrastructure.sh first to create Azure resources"
    exit 1
fi

# Get storage account name from Terraform
STORAGE_NAME=$(terraform output -raw storage_account_name)
RG_NAME=$(terraform output -raw resource_group_name)

echo "Storage Account: $STORAGE_NAME"
echo "Resource Group: $RG_NAME"

# Get storage account key for authentication
echo ""
echo "Retrieving storage account key..."
STORAGE_KEY=$(az storage account keys list \
    --resource-group "$RG_NAME" \
    --account-name "$STORAGE_NAME" \
    --query '[0].value' \
    --output tsv)

# Upload embeddings (pickle files)
echo ""
echo "======================================"
echo "Uploading Embeddings"
echo "======================================"

# Prompt for embeddings directory
read -p "Enter path to directory containing .pkl files (or press Enter to skip): " EMBEDDINGS_DIR

if [ -n "$EMBEDDINGS_DIR" ] && [ -d "$EMBEDDINGS_DIR" ]; then
    echo "Uploading pickle files from: $EMBEDDINGS_DIR"
    
    # Count files to upload
    PKL_COUNT=$(find "$EMBEDDINGS_DIR" -name "*.pkl" | wc -l)
    echo "Found $PKL_COUNT pickle files"
    
    if [ "$PKL_COUNT" -gt 0 ]; then
        az storage blob upload-batch \
            --account-name "$STORAGE_NAME" \
            --account-key "$STORAGE_KEY" \
            --destination embeddings \
            --source "$EMBEDDINGS_DIR" \
            --pattern "*.pkl" \
            --overwrite
        echo "✓ Embeddings uploaded successfully"
    else
        echo "WARNING: No .pkl files found in $EMBEDDINGS_DIR"
    fi
else
    echo "Skipping embeddings upload"
fi

# Upload PDFs
echo ""
echo "======================================"
echo "Uploading PDFs"
echo "======================================"

read -p "Enter path to directory containing PDF files (or press Enter to skip): " PDFS_DIR

if [ -n "$PDFS_DIR" ] && [ -d "$PDFS_DIR" ]; then
    echo "Uploading PDFs from: $PDFS_DIR"
    
    # Count files to upload
    PDF_COUNT=$(find "$PDFS_DIR" -name "*.pdf" | wc -l)
    echo "Found $PDF_COUNT PDF files"
    
    if [ "$PDF_COUNT" -gt 0 ]; then
        az storage blob upload-batch \
            --account-name "$STORAGE_NAME" \
            --account-key "$STORAGE_KEY" \
            --destination pdfs \
            --source "$PDFS_DIR" \
            --pattern "*.pdf" \
            --overwrite
        echo "✓ PDFs uploaded successfully"
    else
        echo "WARNING: No .pdf files found in $PDFS_DIR"
    fi
else
    echo "Skipping PDFs upload"
fi

echo ""
echo "======================================"
echo "Upload Complete!"
echo "======================================"

# Show what's in storage
echo ""
echo "Current contents:"
echo ""
echo "Embeddings container:"
az storage blob list \
    --account-name "$STORAGE_NAME" \
    --account-key "$STORAGE_KEY" \
    --container-name embeddings \
    --output table | head -20

echo ""
echo "PDFs container:"
az storage blob list \
    --account-name "$STORAGE_NAME" \
    --account-key "$STORAGE_KEY" \
    --container-name pdfs \
    --output table | head -20

echo ""
echo "Data is ready! Your RAG system can now query the embeddings."