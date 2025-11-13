#!/bin/bash
# deploy_infrastructure.sh
# Deploys Azure infrastructure using Terraform
# Run this when: Creating infrastructure for first time or modifying .tf files

set -e  # Exit immediately if a command exits with a non-zero status

echo "======================================"
echo "Deploying Infrastructure with Terraform"
echo "======================================"

# Optional: Specify environment (defaults to dev if not provided)
ENVIRONMENT=${1:-dev}
echo "Environment: $ENVIRONMENT"

# Initialize Terraform (safe to run multiple times)
echo ""
echo "Initializing Terraform..."
terraform init

# Validate configuration
echo ""
echo "Validating Terraform configuration..."
terraform validate

# Show what will change
echo ""
echo "Planning infrastructure changes..."
if [ -f "${ENVIRONMENT}.tfvars" ]; then
    echo "Using ${ENVIRONMENT}.tfvars for variable values"
    terraform plan -var-file="${ENVIRONMENT}.tfvars" -out=tfplan
else
    echo "No ${ENVIRONMENT}.tfvars found, using defaults from variables.tf"
    terraform plan -out=tfplan
fi

# Prompt for confirmation
echo ""
read -p "Apply these changes? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    rm tfplan
    exit 0
fi

# Apply the plan
echo ""
echo "Applying infrastructure changes..."
terraform apply tfplan
rm tfplan

# Show outputs
echo ""
echo "======================================"
echo "Deployment Complete! Outputs:"
echo "======================================"
terraform output

echo ""
echo "Next steps:"
echo "1. Run ./deploy_app.sh to deploy your function code"
echo "2. Run ./upload_data.sh to upload embeddings"