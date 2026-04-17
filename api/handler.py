# api/handler.py
# Lambda API — sert les données au dashboard via API Gateway.
# Un seul handler qui route selon le path HTTP.

import os
import json
import logging
import boto3
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "cloudcostpilot-costs")


class DecimalEncoder(json.JSONEncoder):
    """
    DynamoDB retourne des Decimal, mais json.dumps ne sait pas les sérialiser.
    Ce custom encoder convertit Decimal → float pour la réponse JSON.
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def _query(table, pk: str, sk_prefix: str = None) -> list[dict]:
    """Requête DynamoDB par PK, avec filtre optionnel sur le début de SK."""
    if sk_prefix:
        response = table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
            ExpressionAttributeValues={":pk": pk, ":sk": sk_prefix}
        )
    else:
        response = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": pk}
        )
    return response.get("Items", [])


def _response(status_code: int, body: dict) -> dict:
    """Formate la réponse HTTP pour API Gateway."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            # CORS : permet au dashboard (sur Vercel) d'appeler l'API (sur AWS)
            # Sans ces headers, le navigateur bloque la requête (same-origin policy)
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def lambda_handler(event, context):
    """
    Point d'entrée. API Gateway envoie l'événement HTTP.
    event["rawPath"] contient le chemin (ex: "/costs", "/recommendations").
    event["queryStringParameters"] contient les query params (ex: ?month=2026-03).
    """
    path = event.get("rawPath", event.get("path", "/"))
    params = event.get("queryStringParameters") or {}
    logger.info(f"API request: {path} params={params}")

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    # ---- Route: GET /costs ----
    # Retourne les coûts journaliers pour un mois donné
    if path == "/costs":
        month = params.get("month", datetime.now().strftime("%Y-%m"))
        items = _query(table, f"DAILY#{month}")
        return _response(200, {
            "month": month,
            "dailyCosts": items,
            "total": sum(float(i.get("totalCost", 0)) for i in items),
        })

    # ---- Route: GET /costs/by-service ----
    # Retourne les coûts par service pour un jour donné
    elif path == "/costs/by-service":
        date = params.get("date", datetime.now().strftime("%Y-%m-%d"))
        items = _query(table, f"DAILY#{date}")
        return _response(200, {
            "date": date,
            "services": items,
        })

    # ---- Route: GET /costs/by-tag ----
    # Retourne les coûts par tag team pour un mois donné
    elif path == "/costs/by-tag":
        month = params.get("month", datetime.now().strftime("%Y-%m"))
        items = _query(table, f"TAG#{month}")
        return _response(200, {
            "month": month,
            "tagCosts": items,
        })

    # ---- Route: GET /recommendations ----
    # Retourne les recommandations actives
    elif path == "/recommendations":
        items = _query(table, "RECOMMENDATION")
        return _response(200, {
            "recommendations": items,
            "count": len(items),
        })

    # ---- Route: GET /anomalies ----
    # Retourne les anomalies du mois
    elif path == "/anomalies":
        month = params.get("month", datetime.now().strftime("%Y-%m"))
        items = _query(table, f"ANOMALY#{month}")
        return _response(200, {
            "month": month,
            "anomalies": items,
            "count": len(items),
        })

    # ---- Route: GET /health ----
    elif path == "/health":
        return _response(200, {"status": "ok"})

    # ---- 404 ----
    else:
        return _response(404, {"error": f"Route not found: {path}"})
