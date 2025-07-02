output "vm_public_ip" {
  value       = azurerm_public_ip.pip-roy
  depends_on  = [null_resource.validate_ip]
}
