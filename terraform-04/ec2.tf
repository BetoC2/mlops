provider "aws" {
  region = "us-east-2"
}

# Generar clave SSH
resource "tls_private_key" "deployer" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "local_file" "private_key" {
  filename        = "id_rsa"
  content         = tls_private_key.deployer.private_key_pem
  file_permission = "0600"
}

resource "aws_key_pair" "deployer" {
  key_name   = "deployer-key"
  public_key = tls_private_key.deployer.public_key_openssh
}

# Grupo de seguridad
resource "aws_security_group" "pods_security_group" {
  name_prefix = "pods-security-group"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Instancia SLAVE con FastAPI y PyTorch
resource "aws_instance" "slave" {
  ami             = "ami-0d0f28110d16ee7d6"
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.deployer.key_name
  security_groups = [aws_security_group.pods_security_group.name]
  
  root_block_device {
    volume_size = 32
  }
  
  tags = {
    Name = "slave"
  }
}

# Instancia MASTER con NGINX reverse proxy
resource "aws_instance" "master" {
  ami             = "ami-0d0f28110d16ee7d6"
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.deployer.key_name
  security_groups = [aws_security_group.pods_security_group.name]
  tags = {
    Name = "master"
  }
}

output "master_ip" {
  value = aws_instance.master.public_ip
}

output "slave_ip" {
  value = aws_instance.slave.public_ip
}