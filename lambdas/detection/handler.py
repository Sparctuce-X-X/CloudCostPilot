# lambdas/detection/handler.py
# Lambda "detective" — déclenchée quotidiennement par EventBridge.
# Lit les données dans DynamoDB + interroge AWS pour détecter les gaspillages.
# Écrit les recommandations dans DynamoDB et publie sur SNS si anomalie trouvée.

import os
import json
import logging
import boto3
from datetime import datetime
from lambdas.detection.rules import (
    detect_untagged_resources,
    detect_cost_anomalies,
    detect_ebs_orphans,
    detect_unused_eips,
)
from lambdas.ingestion.storage import write_items_to_dynamodb

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "cloudcostpilot-costs")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")


def _query_dynamodb(dynamodb_resource, pk: str) -> list[dict]:
    """Requête DynamoDB par Partition Key."""
    table = dynamodb_resource.Table(TABLE_NAME)
    response = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": pk}
    )
    return response.get("Items", [])


def _publish_to_sns(sns_client, recommendations: list[dict]):
    """Publie un résumé des recommandations sur SNS (email + Slack)."""
    if not SNS_TOPIC_ARN or not recommendations:
        return

    # Construire un message lisible
    lines = [f"CloudCostPilot — {len(recommendations)} recommandation(s) détectée(s)\n"]
    for rec in recommendations:
        severity = rec.get("severity", "?").upper()
        title = rec.get("title", "?")
        desc = rec.get("description", "")
        lines.append(f"[{severity}] {title}")
        lines.append(f"  → {desc}\n")

    message = "\n".join(lines)

    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"CloudCostPilot: {len(recommendations)} alerte(s)",
        Message=message,
    )
    logger.info(f"Published {len(recommendations)} recommendations to SNS")


def lambda_handler(event, context):
    """
    Point d'entrée. Déclenché par EventBridge (cron quotidien).

    L'event EventBridge est simple : {"source": "aws.events", ...}
    On n'a pas besoin de son contenu — on sait juste qu'il est l'heure de scanner.
    """
    logger.info("Detective Lambda started")

    dynamodb = boto3.resource("dynamodb")
    ec2 = boto3.client("ec2")
    sns = boto3.client("sns")

    all_recommendations = []

    # --- 1. Détection basée sur les données CUR (dans DynamoDB) ---

    # Récupérer les coûts par tag du mois en cours
    current_month = datetime.now().strftime("%Y-%m")
    tag_items = _query_dynamodb(dynamodb, f"TAG#{current_month}")
    logger.info(f"Fetched {len(tag_items)} tag cost items")

    untagged_recs = detect_untagged_resources(tag_items)
    all_recommendations.extend(untagged_recs)
    logger.info(f"Untagged resources: {len(untagged_recs)} recommendations")

    # Récupérer les coûts journaliers du mois en cours
    daily_items = _query_dynamodb(dynamodb, f"DAILY#{current_month}")
    logger.info(f"Fetched {len(daily_items)} daily cost items")

    anomaly_recs = detect_cost_anomalies(daily_items)
    all_recommendations.extend(anomaly_recs)
    logger.info(f"Cost anomalies: {len(anomaly_recs)} recommendations")

    # --- 2. Détection basée sur l'API AWS (scan des ressources) ---

    ebs_recs = detect_ebs_orphans(ec2)
    all_recommendations.extend(ebs_recs)
    logger.info(f"EBS orphans: {len(ebs_recs)} recommendations")

    eip_recs = detect_unused_eips(ec2)
    all_recommendations.extend(eip_recs)
    logger.info(f"Unused EIPs: {len(eip_recs)} recommendations")

    # --- 3. Stocker les recommandations dans DynamoDB ---
    if all_recommendations:
        written = write_items_to_dynamodb(dynamodb, TABLE_NAME, all_recommendations)
        logger.info(f"Wrote {written} recommendations to DynamoDB")

        # --- 4. Alerter via SNS ---
        _publish_to_sns(sns, all_recommendations)

    total = len(all_recommendations)
    logger.info(f"Detective Lambda finished: {total} total recommendations")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "recommendations": total,
            "untagged": len(untagged_recs),
            "anomalies": len(anomaly_recs),
            "ebsOrphans": len(ebs_recs),
            "unusedEips": len(eip_recs),
        })
    }
