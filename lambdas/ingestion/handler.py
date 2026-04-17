# lambdas/ingestion/handler.py
# Point d'entrée de la Lambda d'ingestion.
# Déclenchée par un événement S3 : quand AWS dépose un nouveau fichier CUR.

import os
import logging
import boto3
from lambdas.ingestion.parser import parse_cur_from_s3
from lambdas.ingestion.enricher import enrich_all
from lambdas.ingestion.storage import write_items_to_dynamodb

# Logger — tous les print() et logs apparaissent dans CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Nom de la table DynamoDB — passé via variable d'environnement
# (jamais hardcodé, pour pouvoir changer sans modifier le code)
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "cloudcostpilot-costs")


def lambda_handler(event, context):
    """
    Point d'entrée Lambda.

    Args:
        event: L'événement S3 qui a déclenché la Lambda.
               Contient le bucket et la clé du fichier uploadé.
               Structure : event["Records"][0]["s3"]["bucket"]["name"]
                           event["Records"][0]["s3"]["object"]["key"]

        context: Objet Lambda context (request_id, memory_limit, etc.)
                 On ne l'utilise pas ici mais il est toujours passé par AWS.

    Returns:
        Dict avec statusCode et body (convention API Gateway).
    """
    logger.info(f"Lambda triggered with event: {event}")

    # --- 1. Extraire bucket et key depuis l'événement S3 ---
    # Un événement S3 peut contenir plusieurs records (rare mais possible)
    # On traite le premier — en prod on bouclerait sur tous
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    logger.info(f"Processing file: s3://{bucket}/{key}")

    # --- 2. Parser le fichier CUR ---
    s3_client = boto3.client("s3")
    df = parse_cur_from_s3(s3_client, bucket, key)
    logger.info(f"Parsed {len(df)} rows from CUR")

    # --- 3. Enrichir (agrégations) ---
    items = enrich_all(df)
    logger.info(f"Enriched into {len(items)} DynamoDB items")

    # --- 4. Stocker dans DynamoDB ---
    dynamodb = boto3.resource("dynamodb")
    written = write_items_to_dynamodb(dynamodb, TABLE_NAME, items)
    logger.info(f"Wrote {written} items to {TABLE_NAME}")

    return {
        "statusCode": 200,
        "body": f"Processed {len(df)} CUR rows → {written} DynamoDB items"
    }
