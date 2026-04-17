# infra/backend.tf
# Configure le stockage distant du state Terraform.
# Le state = la "mémoire" de Terraform, il sait quelles ressources existent dans AWS.
# Sans remote state, tout est en local → risque de perte, pas de travail en équipe.

terraform {
  backend "s3" {
    bucket         = "cloudcostpilot-tfstate-478442521818"   # Bucket S3 créé manuellement (poule-et-oeuf)
    key            = "infra/terraform.tfstate"               # Chemin du fichier state dans le bucket
    region         = "eu-west-3"
    profile        = "cloudcostpilot"
    dynamodb_table = "cloudcostpilot-tflock"                 # Table DynamoDB pour le locking
    encrypt        = true                                     # Chiffrement du state au repos (SSE-S3)
  }
}
