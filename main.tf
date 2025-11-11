terraform{
    required_providers{
        azurerm = {
            source = "hashicorp/azurerm"
            version = "~> 3.0"
        }
    }
}

provider "azurerm" {
    features {}
}

resource "azurerm_resource_group" "rag" {
    name = "rg-parkinsons-rag"
    location = "West Europe"
}

resource "azurerm_storage_account" "rag" {
    name  = "stparkinsonsrag"
    resource_group_name = azurerm_resource_group.rag.name
    location = azurerm_resource_group.rag.location
    account_tier = "Standard"
    account_replication_type = "LRS"
}

resource "azurerm_storage_container" "pdfs" {
    name = "pdfs"
    storage_account_name = azurerm_storage_account.rag.name
    container_access_type = "private"
}

resource "azurerm_storage_container" "embeddings" {
    name = "embeddings"
    storage_account_name = azurerm_storage_account.rag.name
    container_access_type = "private"
}

resource "azurerm_service_plan" "rag" {
    name = "asp-parkinsons-rag"
    resource_group_name = azurerm_resource_group.rag.name
    location = azurerm_resource_group.rag.location
    os_type = "Linux"
    sku_name = "B1"
}

resource "azurerm_linux_function_app" "rag" {
    name = "func-parkinsons-rag"
    resource_group_name = azurerm_resource_group.rag.name
    location = azurerm_resource_group.rag.location
    service_plan_id = azurerm_service_plan.rag.id
    
    storage_account_name = azurerm_storage_account.rag.name
    storage_account_access_key = azurerm_storage_account.rag.primary_access_key
    
    site_config {
        application_stack {
            python_version = "3.11"
        }
    }
    app_settings = {
        enabled = "false"
    }
}

output "storage_account_name" {
    value = azurerm_storage_account.rag.name
}

output "function_app_name" {
    value = azurerm_linux_function_app.rag.name
}

output "resource_group_name" {
    value = azurerm_resource_group.rag.name
}