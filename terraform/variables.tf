variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "vm-benchmarking-rg"
}

variable "resource_group_location" {
  description = "Azure region"
  type        = string
  default     = "swedencentral"
}
