resource "null_resource" "provision_apache" {
  depends_on = [aws_instance.vm1]
  triggers = {
    always_run = timestamp()
  }

  provisioner "remote-exec" {
    inline = [
      "sudo dnf update -y",
      "sudo dnf install -y httpd",
      "echo '<h1>Welcome to the Web Server!</h1>' | sudo tee /var/www/html/welcome.html",
      "sudo systemctl enable httpd",
      "sudo systemctl start httpd"
    ]

    connection {
      type        = "ssh"
      host        = aws_instance.vm1.public_ip
      user        = var.admin_username
      password    = var.admin_password
      port        = 22
      timeout     = "2m"
      # אפשר גם להשתמש ב-private_key במקום password
      # private_key = file("~/.ssh/id_rsa")
    }
  }
}



output "server_info" {
  value       = "Please browse: http://${aws_instance.vm1.public_ip}/welcome.html"
  description = "Instructions to access the Apache web server."
}
