# infra/provider.tf
# Configure le provider AWS — le "connecteur" entre Terraform et ton compte AWS.

terraform {
  # Déclare quels providers on utilise et leurs versions
  required_providers {
    aws = {
      source  = "hashicorp/aws"    # Provider officiel AWS maintenu par HashiCorp
      version = "~> 5.0"           # ~> 5.0 = accepte 5.x mais pas 6.0 (évite les breaking changes)
    }
  }

  # Version minimale de Terraform requise pour ce projet
  required_version = ">= 1.5"
}

# Configuration de la connexion à AWS
provider "aws" {
  region  = "eu-west-3"           # Paris — le plus proche, moins de latence
  profile = "cloudcostpilot"      # Profil AWS CLI configuré avec nos Access Keys

  # Tags par défaut appliqués à TOUTES les ressources créées par Terraform
  # Bonne pratique FinOps : chaque ressource est taggée automatiquement
  # → apparaîtra dans le CUR pour l'attribution des coûts
  default_tags {
    tags = {
      Project     = "CloudCostPilot"
      ManagedBy   = "Terraform"        # Distingue les ressources Terraform de celles créées manuellement
      Environment = "dev"
    }
  }
}
