provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "my-vpc"

  }
}

resource "aws_subnet" "my_subnet" {
  vpc_id     = aws_vpc.my_vpc.id
  cidr_block = "10.0.0.0/16"
  availability_zone = "us-east-1a"  
  tags = {
    Name = "my-subnet"

  }
}


  

variable "region" {
 default = "us-east-1a"
}


variable "ami" {
 default = "ami-085386e29e44dacd7"
 }
variable "vm_name" {
 default = "vm-roy"
}

variable "admin_username" {
 default = "admin-user"
}

variable "admin_password" {
 default = "Password123!"
}

variable "vm_size" {
 default = "t2.micro"
}