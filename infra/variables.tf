# infra/variables.tf
# Variables Terraform — les valeurs configurables du projet.
# Permet de ne pas hardcoder des valeurs qui changent selon l'environnement.

variable "alert_email" {
  description = "Email qui recevra les alertes FinOps"
  type        = string
  default     = "dmnqhuang@gmail.com"
  # En entreprise, on ne mettrait PAS de default — on forcerait l'utilisateur
  # à fournir la valeur. Ici on simplifie pour le dev.
}
