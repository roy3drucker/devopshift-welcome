provider "azurerm" {
  features {}
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


