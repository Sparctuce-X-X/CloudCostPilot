# lambdas/ingestion/storage.py
# Écrit les items enrichis dans DynamoDB.
# Utilise BatchWriter pour l'efficacité (25 items par requête au lieu de 1).

from decimal import Decimal
from typing import Any


def _convert_floats_to_decimal(item: dict) -> dict:
    """
    DynamoDB n'accepte PAS les float Python (problèmes de précision IEEE 754).
    Il faut convertir en Decimal. C'est un piège classique avec boto3.

    Exemple :
      float 0.1 en Python = 0.1000000000000000055511151231257827021181583404541015625
      Decimal("0.1") = exactement 0.1

    boto3 lèvera une erreur si tu passes un float.
    """
    converted = {}
    for key, value in item.items():
        if isinstance(value, float):
            # round(6) puis str pour éviter les artefacts de conversion
            converted[key] = Decimal(str(round(value, 6)))
        else:
            converted[key] = value
    return converted


def write_items_to_dynamodb(
    dynamodb_resource,
    table_name: str,
    items: list[dict[str, Any]]
) -> int:
    """
    Écrit une liste d'items dans DynamoDB via BatchWriter.

    Pourquoi dynamodb_resource en paramètre ? (injection de dépendance)
    → En test : on passe un resource moto (mock)
    → En prod : on passe boto3.resource("dynamodb")

    Le BatchWriter de boto3 gère automatiquement :
    - Le découpage en lots de 25 items (limite AWS)
    - Le retry avec exponential backoff si DynamoDB throttle
    - La gestion des "unprocessed items"

    Args:
        dynamodb_resource: boto3.resource("dynamodb") réel ou mock
        table_name: Nom de la table DynamoDB
        items: Liste de dicts à écrire

    Returns:
        Nombre d'items écrits
    """
    table = dynamodb_resource.Table(table_name)
    count = 0

    # with batch_writer() → boto3 bufferise et envoie par lots de 25
    # À la sortie du "with", tout ce qui reste dans le buffer est envoyé
    with table.batch_writer() as batch:
        for item in items:
            converted = _convert_floats_to_decimal(item)
            batch.put_item(Item=converted)
            count += 1

    return count
