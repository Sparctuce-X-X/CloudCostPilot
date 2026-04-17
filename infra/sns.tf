# infra/sns.tf
# Topic SNS pour les alertes FinOps.
# SNS = Simple Notification Service : un système pub/sub.
# Tu publies un message → tous les abonnés le reçoivent (email, Slack, SMS...).

resource "aws_sns_topic" "cost_anomalies" {
  name = "cloudcostpilot-cost-anomalies"
  # Coût : $0.00 pour le topic. $0.50 par million de notifications email.
}

# Abonnement email — tu recevras un email pour chaque alerte.
# IMPORTANT : après terraform apply, tu recevras un email de confirmation
# d'AWS. Tu DOIS cliquer "Confirm subscription" sinon les alertes ne partiront pas.
resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.cost_anomalies.arn
  protocol  = "email"
  endpoint  = var.alert_email    # Défini dans variables.tf
}
