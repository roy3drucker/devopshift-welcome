resource "azurerm_linux_virtual_machine" "example" {
}
  name = "vm-machine"
  resource_group_name = azurerm_resource_group.roy-rg.name
  location = azurerm_resource_group.roy-rg.location
  size = "Standard_F2"
  admin_username = "adminuser"
  network_interface_ids = [
    azurerm_network_interface.roy.id,
  ]


resource "aws_instance" "web" {
  # ...

  # Establishes connection to be used by all
  # generic remote provisioners (i.e. file/remote-exec)
  connection {
    type     = "ssh"
    user     = "root"
    password = var.root_password
    host     = self.public_ip
  }

  provisioner "remote-exec" {
    inline = [
      "puppet apply",
      "consul join ${aws_instance.web.private_ip}",
    ]
  }
}
