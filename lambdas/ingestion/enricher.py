# lambdas/ingestion/enricher.py
# Transforme le DataFrame CUR brut en métriques agrégées prêtes pour DynamoDB.
# Chaque fonction retourne une liste de dicts = un item DynamoDB.

import pandas as pd
from datetime import datetime, timedelta
from typing import Any


def compute_daily_totals(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Agrège le coût total par jour.
    Résultat stocké dans DynamoDB avec PK = "DAILY#YYYY-MM", SK = "YYYY-MM-DD".

    Exemple d'item retourné :
    {
        "PK": "DAILY#2026-03",
        "SK": "2026-03-01",
        "totalCost": 12.45,
        "currency": "USD",
        "itemCount": 13,
        "expireAt": 1727740800  (timestamp Unix dans 90 jours)
    }
    """
    # groupby date → somme des coûts + nombre de lignes
    daily = df.groupby(
        df["line_item_usage_start_date"].dt.date
    ).agg(
        totalCost=("line_item_unblended_cost", "sum"),
        itemCount=("line_item_unblended_cost", "count")
    ).reset_index()

    items = []
    for _, row in daily.iterrows():
        date_str = str(row["line_item_usage_start_date"])
        month_str = date_str[:7]  # "2026-03"

        items.append({
            "PK": f"DAILY#{month_str}",
            "SK": date_str,
            "totalCost": round(float(row["totalCost"]), 6),
            "currency": "USD",
            "itemCount": int(row["itemCount"]),
            "expireAt": int((datetime.now() + timedelta(days=90)).timestamp()),
        })

    return items


def compute_service_costs(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Agrège le coût par service pour chaque jour.
    PK = "DAILY#YYYY-MM-DD", SK = nom du service.

    Permet de répondre à : "Combien m'a coûté EC2 le 16 avril ?"
    """
    daily_service = df.groupby([
        df["line_item_usage_start_date"].dt.date,
        "line_item_product_code"
    ]).agg(
        totalCost=("line_item_unblended_cost", "sum"),
        itemCount=("line_item_unblended_cost", "count")
    ).reset_index()

    items = []
    for _, row in daily_service.iterrows():
        date_str = str(row["line_item_usage_start_date"])

        items.append({
            "PK": f"DAILY#{date_str}",
            "SK": row["line_item_product_code"],
            "totalCost": round(float(row["totalCost"]), 6),
            "itemCount": int(row["itemCount"]),
            "expireAt": int((datetime.now() + timedelta(days=90)).timestamp()),
        })

    return items


def compute_tag_costs(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Agrège le coût par tag "team" pour chaque jour.
    PK = "TAG#YYYY-MM", SK = "team#nom_equipe#YYYY-MM-DD".

    Permet de répondre à : "Combien l'équipe backend a dépensé en mars ?"
    """
    daily_tag = df.groupby([
        df["line_item_usage_start_date"].dt.date,
        "resource_tags_user_team"
    ]).agg(
        totalCost=("line_item_unblended_cost", "sum")
    ).reset_index()

    items = []
    for _, row in daily_tag.iterrows():
        date_str = str(row["line_item_usage_start_date"])
        month_str = date_str[:7]
        team = row["resource_tags_user_team"]

        items.append({
            "PK": f"TAG#{month_str}",
            "SK": f"team#{team}#{date_str}",
            "team": team,
            "date": date_str,
            "totalCost": round(float(row["totalCost"]), 6),
            "expireAt": int((datetime.now() + timedelta(days=90)).timestamp()),
        })

    return items


def enrich_all(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Point d'entrée : lance toutes les agrégations et retourne
    la liste complète des items à écrire dans DynamoDB.
    """
    items = []
    items.extend(compute_daily_totals(df))
    items.extend(compute_service_costs(df))
    items.extend(compute_tag_costs(df))
    return items
