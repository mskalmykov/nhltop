terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.63"
    }
  }

  required_version = ">= 0.13.1"

  backend "s3" {
    bucket = "tfstate-mskalmykov-aike2ier"
    key    = "msk-epam-diploma"
    region = "eu-central-1"
  }

}

provider "aws" {
  profile = "default"
  region  = var.AWS_REGION
  default_tags {
    tags = {
      owner = "mikhail_kalmykov@epam.com"
    }
  }
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "msk-epam-diploma"
  cidr = "10.0.0.0/16"

  azs            = ["${var.AWS_REGION}a", "${var.AWS_REGION}b"]
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]

}

module "eks" {
  source           = "terraform-aws-modules/eks/aws"
  cluster_name     = "my_eks"
  cluster_version  = "1.21"
  vpc_id           = module.vpc.vpc_id
  subnets          = module.vpc.public_subnets
  write_kubeconfig = false
  worker_groups = [
    {
      name                 = "worker-group"
      instance_type        = "t3.medium"
      key_name             = "mskawslearn1-pair1"
      asg_desired_capacity = 2
      asg_max_size         = 4
      tags = [
        {
          "key"                 = "k8s.io/cluster-autoscaler/enabled"
          "propagate_at_launch" = "false"
          "value"               = "true"
        },
        {
          "key"                 = "k8s.io/cluster-autoscaler/my_eks"
          "propagate_at_launch" = "false"
          "value"               = "owned"
        }
      ]
    }
  ]
}

data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_id
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

resource "aws_ecr_repository" "nhltop" {
  name = "nhltop"
}

module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 3.0"

  identifier = "my-db"

  engine            = "mariadb"
  engine_version    = "10.5.12"
  instance_class    = "db.t2.micro"
  allocated_storage = 20

  name     = "nhltop"
  username = "nhltop"
  port     = "3306"
  # You should run "export TF_VAR_DB_PASSWORD=xxxxxxx" command
  # prior to "terraform apply" to define this value
  password = var.DB_PASSWORD

  skip_final_snapshot = true

  vpc_security_group_ids = [aws_security_group.sg_rds.id]

  # DB subnet group
  subnet_ids           = module.vpc.public_subnets
  family               = "mariadb10.5"
  major_engine_version = "10.5"

}

resource "aws_security_group" "sg_rds" {
  name        = "RDS security group"
  description = "Allow tcp/3306 from EKS subnets"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "MySQL from EKS subnets"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = module.vpc.public_subnets_cidr_blocks
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

}
