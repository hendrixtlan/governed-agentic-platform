variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "name" {
  type    = string
  default = "governed-agentic-platform"
}

variable "bedrock_model_arn" {
  type        = string
  description = "Approved Bedrock model or inference profile ARN"
  default     = "*"
}
