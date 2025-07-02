provider "azurerm" {
  features {}
}

resource "time_sleep" "wait_for_ip" {
  create_duration = "30s"
}


resource "azurerm_resource_group" "rg-roy" {
  name     = "roy-resources"
  location = var.location
}

resource "azurerm_virtual_network" "vnet-roy" {
  name                = "roy-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.rg-roy.name
}

resource "azurerm_subnet" "subnet-roy" {
  name                 = "roy-subnet"
  resource_group_name  = azurerm_resource_group.rg-roy.name
  virtual_network_name = azurerm_virtual_network.vnet-roy.name
  address_prefixes     = ["10.0.1.0/24"]
}


resource "azurerm_public_ip" "pip-roy" {
  name                = "roy-pip"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg-roy.name
  allocation_method   = "Dynamic"  # Dynamic IP allocation for Basic SKU
  sku = "Basic"  
}


resource "azurerm_network_interface" "nic-roy" {
  name                = "roy-nic"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg-roy.name

  ip_configuration {
    name                          = "roy-ipconfig"
    subnet_id                     = azurerm_subnet.subnet-roy.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip-roy.id
  }
}



resource "null_resource" "validate_ip" {
  provisioner "local-exec" {
    command = <<EOT
   if [ -z "${azurerm_public_ip.pip-roy.ip_address}" ]; then
     echo "ERROR: Public IP address was not assigned." >&2
     exit 1
   fi
 EOT
  }
  depends_on = [time_sleep.wait_for_ip]
}






module "virtual-machine_example_basic" {
  source  = "Azure/virtual-machine/azurerm//examples/basic"
  version = "2.0.0"
}