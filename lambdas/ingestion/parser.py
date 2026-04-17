# lambdas/ingestion/parser.py
# Lit un fichier CUR Parquet et retourne un DataFrame filtré avec les colonnes utiles.

import io
import pandas as pd
import pyarrow.parquet as pq

# Les colonnes du CUR qu'on utilise dans notre projet.
# Le vrai CUR en a 50+ — on ne garde que l'essentiel.
COLUMNS = [
    "line_item_usage_start_date",       # Date d'utilisation (YYYY-MM-DD)
    "line_item_product_code",           # Service AWS (AmazonEC2, AmazonS3...)
    "line_item_operation",              # Opération (RunInstances, PutObject...)
    "line_item_resource_id",            # ID de la ressource (i-0abc123, vol-xxx...)
    "line_item_usage_amount",           # Quantité utilisée (heures, requêtes...)
    "line_item_unblended_cost",         # Coût réel en USD
    "line_item_currency_code",          # Devise (USD)
    "resource_tags_user_team",          # Tag: équipe
    "resource_tags_user_environment",   # Tag: environnement (dev/prod)
    "resource_tags_user_owner",         # Tag: propriétaire
]


def parse_cur_from_s3(s3_client, bucket: str, key: str) -> pd.DataFrame:
    """
    Télécharge un fichier Parquet depuis S3 et le parse.

    Pourquoi on passe s3_client en paramètre au lieu de le créer ici ?
    → Injection de dépendance : en test, on passe un client moto (mock).
      En prod, on passe le vrai client boto3. Le parser ne sait pas
      et ne doit pas savoir d'où vient le client.

    Args:
        s3_client: Client boto3 S3 (réel ou mock)
        bucket: Nom du bucket S3
        key: Chemin du fichier dans le bucket

    Returns:
        DataFrame avec uniquement les colonnes COLUMNS, nettoyé.
    """
    # Télécharge le fichier Parquet en mémoire (pas sur disque)
    # Lambda a un /tmp de 512Mo, mais la RAM est plus rapide
    response = s3_client.get_object(Bucket=bucket, Key=key)
    parquet_bytes = response["Body"].read()

    # pyarrow lit le Parquet et ne charge que les colonnes demandées
    # C'est ici que le format colonne montre son avantage :
    # sur un CUR de 50 colonnes, on ne lit que 10 → 5x moins de RAM
    table = pq.read_table(
        io.BytesIO(parquet_bytes),
        columns=COLUMNS
    )
    df = table.to_pandas()

    # --- Nettoyage ---

    # Supprimer les lignes sans coût (certaines lignes CUR sont des "headers")
    df = df[df["line_item_unblended_cost"] > 0]

    # Convertir la date en type datetime pour les agrégations
    df["line_item_usage_start_date"] = pd.to_datetime(
        df["line_item_usage_start_date"]
    )

    # Remplacer les tags vides par "untagged" pour faciliter la détection
    tag_columns = [col for col in df.columns if col.startswith("resource_tags")]
    for col in tag_columns:
        df[col] = df[col].fillna("untagged").replace("", "untagged")

    return df


def parse_cur_from_file(file_path: str) -> pd.DataFrame:
    """
    Variante pour le développement local : lit un fichier Parquet depuis le disque.
    Même logique de filtrage que parse_cur_from_s3.
    """
    table = pq.read_table(file_path, columns=COLUMNS)
    df = table.to_pandas()

    df = df[df["line_item_unblended_cost"] > 0]
    df["line_item_usage_start_date"] = pd.to_datetime(
        df["line_item_usage_start_date"]
    )

    tag_columns = [col for col in df.columns if col.startswith("resource_tags")]
    for col in tag_columns:
        df[col] = df[col].fillna("untagged").replace("", "untagged")

    return df
