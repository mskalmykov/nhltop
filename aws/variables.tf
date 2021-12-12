variable "DB_PASSWORD" {
  description = "Password for MariaDB user"
  type        = string
}

variable "AWS_REGION" {
  description = "AWS region where to create infrastructure"
  type        = string
  default     = "eu-central-1"
}
