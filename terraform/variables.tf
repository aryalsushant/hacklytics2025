variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket for static assets"
  default     = "hacklytics2025"
}

variable "environment" {
  description = "Environment tag"
  default     = "Dev"
}

variable "vpc_id" {
  description = "The VPC ID where the instance will be deployed"
  type        = string
}

variable "subnet_id" {
  description = "The Subnet ID where the instance will be launched"
  type        = string
}

variable "key_name" {
  description = "The EC2 key pair name to access the instance"
  type        = string
}

variable "ami_id" {
  description = "The AMI ID to use for the instance (e.g., an Amazon Linux 2 AMI)"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "app_port" {
  description = "Port on which the backend app will run"
  default     = 5001
}
