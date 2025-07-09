provider "aws" {
  region = var.region
}

resource "aws_instance" "vm" {
  ami                         = "ami-025a9b1af952cc749"
  instance_type               = "t2.micro"
  subnet_id                   = "subnet-06acd0b316280afeb"  
  associate_public_ip_address = true

  tags = {
    Name = "roy-vm"
  }
}


resource "time_sleep" "wait_for_ip" {
  create_duration = "30s"
}



resource "null_resource" "check_public_ip" {
  provisioner "local-exec" {
    command = <<EOT
      if [ -z "${aws_instance.vm.public_ip}" ]; then
        echo "ERROR: Public IP address was not assigned." >&2
        exit 1
      fi
    EOT
  }

  depends_on = [aws_instance.vm]
}