variable "resource_group_name" {
    type = string
    description = "The name of the resource group"
    default = "ragresourcegroup"
}


variable "storage_account_name" {
    type = string
    description = "The name of the storage account"
    default = "ragstoragecolm2024"

    validation {
        condition = length(var.storage_account_name) >= 3 && length(var.storage_account_name) <= 24 && can(regex("^[a-z0-9]+$", var.storage_account_name))
        error_message = "Storage account name must be between 3 and 24 characters long and can only contain lowercase letters and numbers."
    }
}

variable "storage_account_location" {
    type = string
    description = "The location of the storage account"
    default = "West Europe"

}


