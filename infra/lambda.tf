# infra/lambda.tf
# Lambda d'ingestion CUR : déclenchée quand un nouveau fichier arrive dans S3.

# -------------------------------------------------------------------
# 1. Uploader le .zip dans le bucket artifacts
# On utilise aws_s3_object pour que Terraform gère le cycle de vie.
# source_hash = si le contenu du zip change, Terraform re-uploade.
# -------------------------------------------------------------------
resource "aws_s3_object" "ingestion_zip" {
  bucket = aws_s3_bucket.lambda_artifacts.id
  key    = "lambdas/ingestion.zip"
  source = "${path.module}/../build/ingestion.zip"

  # etag = empreinte du fichier. Si le zip change, Terraform détecte le changement.
  etag = filemd5("${path.module}/../build/ingestion.zip")
}

# -------------------------------------------------------------------
# 2. La Lambda elle-même
# -------------------------------------------------------------------
resource "aws_lambda_function" "ingestion" {
  function_name = "cloudcostpilot-ingestion"

  # On pointe vers le .zip dans S3 (pas un fichier local)
  s3_bucket = aws_s3_bucket.lambda_artifacts.id
  s3_key    = aws_s3_object.ingestion_zip.key

  # source_code_hash = permet à Terraform de détecter quand le code a changé
  # sans ça, terraform apply ne mettrait pas à jour la Lambda même si le zip change
  source_code_hash = filebase64sha256("${path.module}/../build/ingestion.zip")

  # Runtime Python 3.11 — doit matcher le Layer
  runtime = "python3.11"

  # Handler = chemin vers la fonction d'entrée
  # Format : module.path.fonction
  # "lambdas.ingestion.handler" = dossier lambdas/ingestion/handler.py
  # "lambda_handler" = la fonction dans ce fichier
  handler = "lambdas.ingestion.handler.lambda_handler"

  # Le rôle IAM qu'on a créé dans iam.tf
  role = aws_iam_role.lambda_role.arn

  # Timeout : 60 secondes max. Le parsing d'un petit CUR prend ~5s.
  # Par défaut Lambda timeout à 3s — trop court pour nous.
  timeout = 60

  # Mémoire : 256 Mo. pandas + pyarrow ont besoin de RAM pour parser le Parquet.
  # 128Mo (défaut) serait trop juste. 256Mo est un bon compromis coût/performance.
  # Coût : $0.0000041667 par seconde à 256Mo → ~$0.00025 par invocation de 60s
  memory_size = 256

  # Variables d'environnement accessibles dans le code via os.environ
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.costs.name
    }
  }

  # Layer AWS SDK Pandas — contient pandas, pyarrow, numpy
  # Fourni gratuitement par AWS, maintenu officiellement
  layers = [
    "arn:aws:lambda:eu-west-3:336392948345:layer:AWSSDKPandas-Python311:25"
  ]
}

# -------------------------------------------------------------------
# 3. Permission pour S3 de déclencher la Lambda
# Sans cette permission, S3 ne peut pas invoquer la Lambda (même si
# la notification est configurée). C'est un mécanisme de sécurité AWS :
# chaque service doit être explicitement autorisé à invoquer une Lambda.
# -------------------------------------------------------------------
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::cloudcostpilot-cur-reports-478442521818"
}

# -------------------------------------------------------------------
# 4. Notification S3 → Lambda
# "Quand un fichier .parquet est créé dans le bucket CUR, déclenche la Lambda"
# C'est le trigger event-driven : pas de polling, pas de cron, juste une réaction.
# -------------------------------------------------------------------
resource "aws_s3_bucket_notification" "cur_trigger" {
  bucket = "cloudcostpilot-cur-reports-478442521818"

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingestion.arn
    events              = ["s3:ObjectCreated:*"]        # Tout nouveau fichier
    filter_prefix       = "cur/"                         # Uniquement dans le dossier cur/
    filter_suffix       = ".parquet"                     # Uniquement les fichiers .parquet
  }

  # La permission doit exister AVANT la notification
  depends_on = [aws_lambda_permission.allow_s3]
}
