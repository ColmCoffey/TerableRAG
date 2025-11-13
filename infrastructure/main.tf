resource "azurerm_resource_group" "rag" {
    name = var.resource_group_name
    location = var.storage_account_location
}

resource "azurerm_storage_account" "rag" {
    name  = var.storage_account_name
    resource_group_name = azurerm_resource_group.rag.name
    location = var.storage_account_location
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
        "functionTimeout" = "00:10:00"
        "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.rag.primary_connection_string
        "FUNCTIONS_WORKER_RUNTIME" = "python"
        }
    }