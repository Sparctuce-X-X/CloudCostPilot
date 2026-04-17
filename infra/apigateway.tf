# infra/apigateway.tf
# API Gateway HTTP API + Lambda API.
# HTTP API (v2) est moins cher que REST API (v1) : $1.00/million vs $3.50/million.
# Pour une API simple comme la nôtre, HTTP API suffit largement.

# -------------------------------------------------------------------
# 1. Upload du .zip API
# -------------------------------------------------------------------
resource "aws_s3_object" "api_zip" {
  bucket = aws_s3_bucket.lambda_artifacts.id
  key    = "lambdas/api.zip"
  source = "${path.module}/../build/api.zip"
  etag   = filemd5("${path.module}/../build/api.zip")
}

# -------------------------------------------------------------------
# 2. Lambda API
# -------------------------------------------------------------------
resource "aws_lambda_function" "api" {
  function_name    = "cloudcostpilot-api"
  s3_bucket        = aws_s3_bucket.lambda_artifacts.id
  s3_key           = aws_s3_object.api_zip.key
  source_code_hash = filebase64sha256("${path.module}/../build/api.zip")
  runtime          = "python3.11"
  handler          = "api.handler.lambda_handler"
  role             = aws_iam_role.lambda_role.arn
  timeout          = 30
  memory_size      = 128    # L'API ne fait que lire DynamoDB → 128Mo suffit

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.costs.name
    }
  }
}

# -------------------------------------------------------------------
# 3. API Gateway HTTP API
# C'est le "routeur" qui reçoit les requêtes HTTPS et les envoie à la Lambda.
# -------------------------------------------------------------------
resource "aws_apigatewayv2_api" "main" {
  name          = "cloudcostpilot-api"
  protocol_type = "HTTP"

  # CORS configuré au niveau de l'API Gateway
  # Permet au dashboard (vercel.app) d'appeler l'API (amazonaws.com)
  cors_configuration {
    allow_origins = ["*"]           # En prod, on restreindrait au domaine Vercel
    allow_methods = ["GET", "OPTIONS"]
    allow_headers = ["Content-Type"]
    max_age       = 3600            # Cache les preflight requests pendant 1h
  }
}

# -------------------------------------------------------------------
# 4. Intégration Lambda — connecte API Gateway à la Lambda
# -------------------------------------------------------------------
resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.main.id
  integration_type   = "AWS_PROXY"    # API Gateway passe tout l'événement HTTP à Lambda
  integration_uri    = aws_lambda_function.api.invoke_arn
  integration_method = "POST"         # API Gateway invoque toujours Lambda en POST (interne)
  payload_format_version = "2.0"      # Format v2 = plus propre (rawPath, queryStringParameters)
}

# -------------------------------------------------------------------
# 5. Route catch-all — toutes les requêtes GET passent par notre Lambda
# La Lambda elle-même fait le routing selon le path.
# -------------------------------------------------------------------
resource "aws_apigatewayv2_route" "catch_all" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /{proxy+}"         # {proxy+} = match tout après GET /
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Route pour GET / (le catch-all ne matche pas la racine)
resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# -------------------------------------------------------------------
# 6. Stage — déploiement auto
# Un "stage" en API Gateway = un environnement (dev, staging, prod).
# $default = le stage par défaut, auto-deployed.
# -------------------------------------------------------------------
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true    # Chaque changement est déployé automatiquement
}

# -------------------------------------------------------------------
# 7. Permission pour API Gateway de déclencher la Lambda
# -------------------------------------------------------------------
resource "aws_lambda_permission" "allow_apigateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# -------------------------------------------------------------------
# 8. Output — l'URL de l'API (on en aura besoin pour le dashboard)
# -------------------------------------------------------------------
output "api_url" {
  value       = aws_apigatewayv2_stage.default.invoke_url
  description = "URL de l'API CloudCostPilot"
}
