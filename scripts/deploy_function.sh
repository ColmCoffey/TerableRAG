# deploy_app.sh - Run this after code changes
#!/bin/bash
set -e  # Exit on error

echo "Packaging function code..."
rm -rf deploy_package function.zip
mkdir deploy_package
cp function_app.py deploy_package/
cp requirements.txt deploy_package/

cd deploy_package
zip -r ../function.zip .
cd ..

echo "Deploying to Azure..."
FUNC_NAME=$(terraform output -raw function_app_name)
RG_NAME=$(terraform output -raw resource_group_name)

az functionapp deployment source config-zip \
  --resource-group $RG_NAME \
  --name $FUNC_NAME \
  --src function.zip

echo "Deployment complete!"