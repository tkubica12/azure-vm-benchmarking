locals {
  vm_config = yamldecode(file("${path.module}/../config.yaml"))
}

resource "azurerm_network_interface" "nic" {
  for_each            = local.vm_config.vms
  name                = "${each.key}-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

# resource "azurerm_linux_virtual_machine" "vm" {
#   for_each                        = local.vm_config.vms
#   name                            = each.key
#   resource_group_name             = azurerm_resource_group.rg.name
#   location                        = azurerm_resource_group.rg.location
#   size                            = each.value.sku_name
#   admin_username                  = "azureuser"
#   admin_password                  = "Azure12345678"
#   disable_password_authentication = false

#   network_interface_ids = [
#     azurerm_network_interface.nic[each.key].id,
#   ]

#   os_disk {
#     name                 = "${each.key}-osdisk"
#     caching              = "ReadOnly"
#     storage_account_type = "Premium_LRS"

#     diff_disk_settings {
#       option    = "Local"
#       placement = can(regex("v5", each.value.sku_name)) ? "ResourceDisk" : "CacheDisk"
#     }
#   }

#   source_image_reference {
#     publisher = "Canonical"
#     offer     = "ubuntu-24_04-lts"
#     sku       = can(regex("p", each.value.sku_name)) ? "server-arm64" : "server"
#     version   = "latest"
#   }

#   boot_diagnostics {}

#   identity {
#     type = "SystemAssigned"
#   }
# }

resource "azapi_resource" "vm" {
  for_each  = local.vm_config.vms
  type      = "Microsoft.Compute/virtualMachines@2024-07-01"
  name      = each.key
  location  = azurerm_resource_group.rg.location
  parent_id = azurerm_resource_group.rg.id

  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {
      hardwareProfile = {
        vmSize = each.value.sku_name
      }
      osProfile = {
        computerName  = each.key
        adminUsername = "azureuser"
        adminPassword = "Azure12345678"
        linuxConfiguration = {
          disablePasswordAuthentication = false
        }
      }
      networkProfile = {
        networkInterfaces = [
          {
            id = azurerm_network_interface.nic[each.key].id
          }
        ]
      }
      storageProfile = {
        osDisk = {
          name         = "${each.key}-osdisk"
          caching      = "ReadOnly"
          createOption = "FromImage"
          managedDisk = {
            storageAccountType = "Premium_LRS"
          }
          diffDiskSettings = {
            option    = "Local"
            placement = can(regex("v6", each.value.sku_name)) ? "NvmeDisk" : "ResourceDisk"
          }
        }
        imageReference = {
          publisher = "Canonical"
          offer     = "ubuntu-24_04-lts"
          sku       = can(regex("p", each.value.sku_name)) ? "server-arm64" : "server"
          version   = "latest"
        }
      }
      diagnosticsProfile = {
        bootDiagnostics = {
          enabled = true
        }
      }
    }
  }
}


