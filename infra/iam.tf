# infra/iam.tf
# IAM Role pour les Lambdas CloudCostPilot.
# Principe du moindre privilège : chaque permission est ciblée sur une ressource précise.

# -------------------------------------------------------------------
# 1. Le RÔLE lui-même + sa Trust Policy
# "Qui a le droit d'assumer ce rôle ?" → uniquement le service Lambda
# -------------------------------------------------------------------
resource "aws_iam_role" "lambda_role" {
  name = "cloudcostpilot-lambda-role"

  # assume_role_policy = Trust Policy (en JSON)
  # "Principal" : qui peut assumer ce rôle
  # "Action" : sts:AssumeRole = le mécanisme d'assumption de rôle dans AWS
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"    # Seul Lambda peut utiliser ce rôle
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# -------------------------------------------------------------------
# 2. Permission Policy — Lecture S3 (bucket CUR)
# La Lambda d'ingestion doit lire les fichiers CUR dans S3.
# On autorise GetObject + ListBucket UNIQUEMENT sur le bucket CUR.
# -------------------------------------------------------------------
resource "aws_iam_role_policy" "lambda_s3_read" {
  name = "s3-read-cur"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",       # Lire un fichier
          "s3:ListBucket"       # Lister les fichiers du bucket
        ]
        Resource = [
          "arn:aws:s3:::cloudcostpilot-cur-reports-478442521818",      # Le bucket lui-même (pour ListBucket)
          "arn:aws:s3:::cloudcostpilot-cur-reports-478442521818/*"     # Les objets dans le bucket (pour GetObject)
        ]
      }
    ]
  })
}

# -------------------------------------------------------------------
# 3. Permission Policy — Écriture DynamoDB
# La Lambda écrit les données enrichies dans la table costs.
# On autorise PutItem + BatchWriteItem + Query (pour vérifier l'idempotence).
# -------------------------------------------------------------------
resource "aws_iam_role_policy" "lambda_dynamodb_write" {
  name = "dynamodb-write-costs"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",           # Écrire un item
          "dynamodb:BatchWriteItem",    # Écrire jusqu'à 25 items d'un coup
          "dynamodb:Query",             # Lire par PK + SK (pour le dashboard aussi)
          "dynamodb:GetItem"            # Lire un item précis
        ]
        # On référence la table via Terraform au lieu de hardcoder l'ARN
        # aws_dynamodb_table.costs.arn = l'ARN réel généré par AWS
        Resource = aws_dynamodb_table.costs.arn
      }
    ]
  })
}

# -------------------------------------------------------------------
# 4. Permission Policy — CloudWatch Logs
# TOUTE Lambda a besoin d'écrire ses logs dans CloudWatch.
# Sans ça, tu ne vois aucun print() ni aucune erreur.
# C'est la permission "de base" que 100% des Lambdas ont.
# -------------------------------------------------------------------
resource "aws_iam_role_policy" "lambda_cloudwatch_logs" {
  name = "cloudwatch-logs"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",      # Créer le groupe de logs (une fois)
          "logs:CreateLogStream",     # Créer un flux de logs (à chaque invocation)
          "logs:PutLogEvents"         # Écrire les lignes de log
        ]
        # /aws/lambda/* = tous les groupes de logs Lambda de notre compte
        # En prod on ciblerait le groupe exact, ici on simplifie légèrement
        Resource = "arn:aws:logs:eu-west-3:478442521818:*"
      }
    ]
  })
}

# -------------------------------------------------------------------
# 5. Permission Policy — EC2 describe (pour détecter EBS orphelins et EIP)
# Actions en lecture seule : describe ne modifie rien.
# -------------------------------------------------------------------
resource "aws_iam_role_policy" "lambda_ec2_read" {
  name = "ec2-describe"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeVolumes",       # Lister les volumes EBS
          "ec2:DescribeAddresses"      # Lister les Elastic IPs
        ]
        Resource = "*"   # Les actions Describe ne supportent pas le filtrage par ARN
      }
    ]
  })
}

# -------------------------------------------------------------------
# 6. Permission Policy — SNS publish (pour envoyer les alertes)
# -------------------------------------------------------------------
resource "aws_iam_role_policy" "lambda_sns_publish" {
  name = "sns-publish"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "sns:Publish"
        Resource = aws_sns_topic.cost_anomalies.arn
      }
    ]
  })
}
