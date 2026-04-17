# infra/s3.tf
# Bucket S3 pour stocker les artifacts de déploiement (code Lambda zippé).

# -------------------------------------------------------------------
# La ressource aws_s3_bucket crée un bucket S3.
# "lambda_artifacts" est le nom TERRAFORM (local, pour référencer dans le code).
# Le vrai nom AWS est défini par "bucket".
# -------------------------------------------------------------------
resource "aws_s3_bucket" "lambda_artifacts" {
  bucket = "cloudcostpilot-artifacts-478442521818"

  # force_destroy = false (par défaut)
  # → Terraform REFUSE de supprimer le bucket s'il contient des fichiers.
  # En prod c'est ce qu'on veut : éviter de supprimer des données par accident.
  # Si tu mets true, terraform destroy videra et supprimera le bucket sans demander.
}

# -------------------------------------------------------------------
# Versioning : garde un historique de chaque fichier uploadé.
# Si on upload un nouveau .zip de Lambda, l'ancien reste accessible.
# Utile pour rollback : "la nouvelle version a un bug, je redéploie l'ancienne".
# -------------------------------------------------------------------
resource "aws_s3_bucket_versioning" "lambda_artifacts" {
  bucket = aws_s3_bucket.lambda_artifacts.id    # Référence au bucket créé au-dessus

  versioning_configuration {
    status = "Enabled"
  }
}

# -------------------------------------------------------------------
# Bloquer TOUT accès public au bucket.
# Nos .zip de Lambda n'ont aucune raison d'être accessibles sur Internet.
# C'est une règle de sécurité de base — AWS le recommande sur tous les buckets.
# -------------------------------------------------------------------
resource "aws_s3_bucket_public_access_block" "lambda_artifacts" {
  bucket = aws_s3_bucket.lambda_artifacts.id

  block_public_acls       = true    # Empêche d'ajouter des ACL publiques
  block_public_policy     = true    # Empêche d'ajouter des bucket policies publiques
  ignore_public_acls      = true    # Ignore les ACL publiques existantes
  restrict_public_buckets = true    # Restreint l'accès public même si une policy l'autorise
}
