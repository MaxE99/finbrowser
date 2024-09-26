terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.21.0"
    }
  }

  backend "s3" {
    bucket  = "ebird-terraform-state-bucket"
    key     = "finbrowser-terraform.tfstate"
    region  = "us-east-2"
    encrypt = true
  }
}

provider "aws" {
  region = "us-east-2"
}
