# infra/detection.tf
# Lambda detective + EventBridge scheduler + permissions.

# -------------------------------------------------------------------
# 1. Upload du .zip detection
# -------------------------------------------------------------------
resource "aws_s3_object" "detection_zip" {
  bucket = aws_s3_bucket.lambda_artifacts.id
  key    = "lambdas/detection.zip"
  source = "${path.module}/../build/detection.zip"
  etag   = filemd5("${path.module}/../build/detection.zip")
}

# -------------------------------------------------------------------
# 2. Lambda detective
# -------------------------------------------------------------------
resource "aws_lambda_function" "detection" {
  function_name    = "cloudcostpilot-detection"
  s3_bucket        = aws_s3_bucket.lambda_artifacts.id
  s3_key           = aws_s3_object.detection_zip.key
  source_code_hash = filebase64sha256("${path.module}/../build/detection.zip")
  runtime          = "python3.11"
  handler          = "lambdas.detection.handler.lambda_handler"
  role             = aws_iam_role.lambda_role.arn
  timeout          = 120    # 2 min — les appels EC2 describe peuvent être lents
  memory_size      = 256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.costs.name
      SNS_TOPIC_ARN  = aws_sns_topic.cost_anomalies.arn
    }
  }
}

# -------------------------------------------------------------------
# 3. EventBridge — scheduler quotidien
# Cron : tous les jours à 8h UTC (10h heure Paris)
# C'est comme un cron Linux mais géré par AWS, serverless, gratuit.
# -------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "daily_detection" {
  name                = "cloudcostpilot-daily-detection"
  description         = "Déclenche la détection de gaspillages chaque matin"
  schedule_expression = "cron(0 8 * * ? *)"
  # Format cron AWS : min heure jour-du-mois mois jour-de-la-semaine année
  # "0 8 * * ? *" = à 8h00 UTC, tous les jours
  # Le "?" est obligatoire sur un des deux champs jour (AWS spécifique)
}

resource "aws_cloudwatch_event_target" "detection_target" {
  rule      = aws_cloudwatch_event_rule.daily_detection.name
  target_id = "detection-lambda"
  arn       = aws_lambda_function.detection.arn
}

# Permission pour EventBridge de déclencher la Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.detection.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_detection.arn
}
