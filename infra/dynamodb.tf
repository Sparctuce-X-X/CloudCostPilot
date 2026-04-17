# infra/dynamodb.tf
# Table DynamoDB pour stocker les données de coûts enrichies.
# C'est la couche "hot access" — le dashboard et l'API lisent ici (réponse <10ms).

resource "aws_dynamodb_table" "costs" {
  name = "cloudcostpilot-costs"

  # ---------------------------------------------------------------
  # billing_mode = "PAY_PER_REQUEST" (on-demand)
  # Tu paies uniquement ce que tu consommes : $1.25 par million d'écritures,
  # $0.25 par million de lectures. Pour notre volume (~100 écritures/jour),
  # c'est quasi gratuit.
  #
  # L'alternative serait "PROVISIONED" : tu réserves X écritures/sec.
  # Moins cher si tu connais ton trafic à l'avance, mais tu paies
  # même quand tu n'utilises pas. Pour un projet dev → on-demand.
  # ---------------------------------------------------------------
  billing_mode = "PAY_PER_REQUEST"

  # ---------------------------------------------------------------
  # hash_key = Partition Key (PK)
  # C'est la clé de distribution : DynamoDB répartit les données
  # sur plusieurs serveurs en fonction de cette clé.
  #
  # range_key = Sort Key (SK)
  # Permet de trier et filtrer à l'intérieur d'une partition.
  # Ensemble, PK + SK forment la clé primaire unique.
  # ---------------------------------------------------------------
  hash_key  = "PK"
  range_key = "SK"

  # On déclare uniquement les attributs utilisés dans les clés.
  # Les autres colonnes (amount, currency, tags...) sont ajoutées
  # librement à l'écriture — DynamoDB est schemaless.
  attribute {
    name = "PK"
    type = "S"    # S = String, N = Number, B = Binary
  }

  attribute {
    name = "SK"
    type = "S"
  }

  # ---------------------------------------------------------------
  # TTL (Time To Live) : supprime automatiquement les items expirés.
  # On mettra un timestamp Unix dans l'attribut "expireAt".
  # Exemple : données de plus de 90 jours supprimées automatiquement.
  # Coût de la suppression TTL : GRATUIT (AWS ne facture pas les deletes TTL).
  # ---------------------------------------------------------------
  ttl {
    attribute_name = "expireAt"
    enabled        = true
  }

  # Les tags du provider (Project, ManagedBy, Environment)
  # sont appliqués automatiquement via default_tags.
}
