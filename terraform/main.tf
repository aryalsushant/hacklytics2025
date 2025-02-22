terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

#############################
# S3 Bucket for Static Assets (Optional)
#############################

resource "aws_s3_bucket" "app_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = var.bucket_name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_website_configuration" "bucket_website" {
  bucket = aws_s3_bucket.app_bucket.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_ownership_controls" "bucket_ownership" {
  bucket = aws_s3_bucket.app_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "bucket_public_access" {
  bucket = aws_s3_bucket.app_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.app_bucket.id
  acl    = "public-read"

  depends_on = [
    aws_s3_bucket_ownership_controls.bucket_ownership,
    aws_s3_bucket_public_access_block.bucket_public_access
  ]
}

#############################
# EC2 Instance for the Backend App
#############################

resource "aws_security_group" "app_sg" {
  name        = "drug-interaction-app-sg"
  description = "Allow traffic on port 5001 (backend app)"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow HTTP traffic"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app_instance" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  subnet_id              = var.subnet_id

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    # Install Python 3.9 and git on Amazon Linux 2
    amazon-linux-extras enable python3.9
    yum install -y python3.9 git
    python3.9 -m pip install --upgrade pip
    cd /home/ec2-user
    # Clone your repository; replace with your actual repo URL.
    git clone https://github.com/yourusername/your_project.git
    cd your_project
    python3.9 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    # Start your app (this command may need to be adapted for your app)
    nohup python app.py > app.log 2>&1 &
  EOF

  tags = {
    Name = "DrugInteractionBackend"
  }
}

output "instance_public_ip" {
  value = aws_instance.app_instance.public_ip
}
