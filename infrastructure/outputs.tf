output "storage_account_name" {
    value = azurerm_storage_account.rag.name
}

output "function_app_name" {
    value = azurerm_linux_function_app.rag.name
}

output "resource_group_name" {
    value = azurerm_resource_group.rag.name
}