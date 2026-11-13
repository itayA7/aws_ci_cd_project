provider "aws" {
  region = "il-central-1"
}


module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "terraform-aws-vpc"
  cidr = "192.168.0.0/16"

  azs             = ["il-central-1a", "il-central-1b", ]
  private_subnets = ["192.168.1.0/24", "192.168.2.0/24"]
  public_subnets  = ["192.168.11.0/24", "192.168.12.0/24"]

  #NAT Gateway configuration
  enable_nat_gateway     = true
  one_nat_gateway_per_az = false
  single_nat_gateway     = true




  enable_vpn_gateway = false


  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}


