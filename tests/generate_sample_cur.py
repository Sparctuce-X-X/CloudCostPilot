# tests/generate_sample_cur.py
# Génère un fichier CUR (Cost & Usage Report) fictif au format Parquet.
# Ce fichier sert pour le développement et les tests, sans attendre le vrai CUR d'AWS.

import pandas as pd
from datetime import datetime, timedelta
import random

# Graine pour reproductibilité des tests
random.seed(42)

# ---------------------------------------------------------------
# Ressources AWS réalistes avec leurs opérations typiques.
# Le vrai CUR a 50+ colonnes — on simule les 10 essentielles.
# Plus la liste est variée, plus les graphiques et la détection
# FinOps seront pertinents dans le dashboard.
# ---------------------------------------------------------------

SERVICES = [
    # === EC2 — différentes instances de différentes équipes ===
    ("AmazonEC2", "RunInstances:t3.large", "i-0abc123def456"),       # backend prod
    ("AmazonEC2", "RunInstances:t3.medium", "i-0def789ghi012"),       # data dev
    ("AmazonEC2", "RunInstances:m5.xlarge", "i-0ghi345jkl678"),       # data prod (gros)
    ("AmazonEC2", "RunInstances:t3.small", "i-0jkl901mno234"),        # frontend prod
    ("AmazonEC2", "RunInstances:t3.micro", "i-0mno567pqr890"),        # mobile dev
    ("AmazonEC2", "NatGateway", "nat-0aaa111bbb222"),                 # infra prod
    ("AmazonEC2", "NatGateway", "nat-0ccc333ddd444"),                 # infra prod (2e AZ)
    ("AmazonEC2", "DataTransfer-Out-Bytes", "i-0abc123def456"),       # transfer sortant

    # === S3 — buckets variés ===
    ("AmazonS3", "PutObject", "my-app-bucket"),
    ("AmazonS3", "GetObject", "my-app-bucket"),
    ("AmazonS3", "PutObject", "ml-training-data"),                    # data science (gros)
    ("AmazonS3", "StorageStandard", "ml-training-data"),
    ("AmazonS3", "PutObject", "user-uploads-prod"),
    ("AmazonS3", "GetObject", "user-uploads-prod"),
    ("AmazonS3", "PutObject", "logs-archive"),                        # security compliance

    # === DynamoDB — tables diverses ===
    ("AmazonDynamoDB", "PayPerRequestThroughput", "users-table"),
    ("AmazonDynamoDB", "PayPerRequestThroughput", "sessions-table"),
    ("AmazonDynamoDB", "PayPerRequestThroughput", "orders-table"),

    # === Lambda — plusieurs fonctions ===
    ("AWSLambda", "Invoke", "process-orders"),
    ("AWSLambda", "Invoke", "send-notifications"),
    ("AWSLambda", "Invoke", "image-thumbnail"),                       # mobile
    ("AWSLambda", "Invoke", "ml-inference"),                          # data science
    ("AWSLambda", "Invoke", "audit-logs"),                            # security

    # === RDS — bases relationnelles ===
    ("AmazonRDS", "InstanceUsage:db.t3.medium", "db-prod-postgres"),
    ("AmazonRDS", "InstanceUsage:db.t3.small", "db-analytics-mysql"), # data

    # === Réseau & load balancers ===
    ("ElasticLoadBalancing", "LoadBalancerUsage", "app-alb"),
    ("ElasticLoadBalancing", "LoadBalancerUsage", "api-alb"),
    ("AmazonCloudFront", "DataTransfer-Out", "distribution-webapp"),
    ("AmazonAPIGateway", "ApiGatewayRequest", "prod-api"),

    # === Services managés ===
    ("AmazonCloudWatch", "PutLogEvents", ""),
    ("AmazonSNS", "Publish-email", "alerts-topic"),
    ("AmazonSQS", "Requests", "jobs-queue"),
    ("AmazonElastiCache", "NodeUsage:cache.t3.micro", "redis-sessions"),

    # === GASPILLAGES — ressources suspectes (non taguées) ===
    ("AmazonEBS", "VolumeUsage", "vol-orphan-001"),                   # EBS orphelin 50Go
    ("AmazonEBS", "VolumeUsage", "vol-orphan-002"),                   # EBS orphelin 100Go
    ("AmazonEBS", "VolumeUsage", "vol-orphan-003"),                   # EBS orphelin 200Go (gros gaspillage)
    ("AmazonEIP", "ElasticIP:IdleAddress", "eip-unused-001"),         # EIP non utilisée
    ("AmazonEIP", "ElasticIP:IdleAddress", "eip-unused-002"),         # EIP non utilisée (2)
    ("AmazonEIP", "ElasticIP:IdleAddress", "eip-unused-003"),         # EIP non utilisée (3)
    ("AmazonEC2", "RunInstances:t3.xlarge", "i-0zombie999"),          # Instance oubliée
    ("AmazonEC2", "RunInstances:m5.large", "i-0ghost-staging"),       # Staging oublié
    ("AmazonS3", "StorageStandard", "legacy-backups-bucket"),         # Bucket legacy sans owner
    ("ElasticLoadBalancing", "LoadBalancerUsage", "old-alb-v1"),      # Ancien LB non supprimé
    ("AmazonRDS", "InstanceUsage:db.t3.small", "db-test-forgotten"),  # RDS de test jamais éteint
]

# ---------------------------------------------------------------
# Tags réalistes avec 5 équipes + environnements + owners.
# Certaines ressources n'ont PAS de tags → la détection FinOps
# va les repérer comme "untagged" dans le dashboard.
# ---------------------------------------------------------------
TAGS = {
    # Équipe backend
    "i-0abc123def456":    {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "my-app-bucket":      {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "users-table":        {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "sessions-table":     {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "orders-table":       {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "process-orders":     {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "send-notifications": {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "prod-api":           {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "api-alb":            {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "redis-sessions":     {"Team": "backend",       "Environment": "prod", "Owner": "alice"},
    "jobs-queue":         {"Team": "backend",       "Environment": "prod", "Owner": "alice"},

    # Équipe data / data science
    "i-0def789ghi012":    {"Team": "data",          "Environment": "dev",  "Owner": "bob"},
    "i-0ghi345jkl678":    {"Team": "data",          "Environment": "prod", "Owner": "bob"},
    "db-prod-postgres":   {"Team": "data",          "Environment": "prod", "Owner": "bob"},
    "db-analytics-mysql": {"Team": "data",          "Environment": "prod", "Owner": "bob"},
    "ml-training-data":   {"Team": "data",          "Environment": "prod", "Owner": "charlie"},
    "ml-inference":       {"Team": "data",          "Environment": "prod", "Owner": "charlie"},

    # Équipe frontend
    "i-0jkl901mno234":    {"Team": "frontend",      "Environment": "prod", "Owner": "diana"},
    "app-alb":            {"Team": "frontend",      "Environment": "prod", "Owner": "diana"},
    "distribution-webapp":{"Team": "frontend",      "Environment": "prod", "Owner": "diana"},
    "user-uploads-prod":  {"Team": "frontend",      "Environment": "prod", "Owner": "diana"},

    # Équipe mobile
    "i-0mno567pqr890":    {"Team": "mobile",        "Environment": "dev",  "Owner": "eve"},
    "image-thumbnail":    {"Team": "mobile",        "Environment": "prod", "Owner": "eve"},

    # Équipe infra / platform
    "nat-0aaa111bbb222":  {"Team": "infra",         "Environment": "prod", "Owner": "frank"},
    "nat-0ccc333ddd444":  {"Team": "infra",         "Environment": "prod", "Owner": "frank"},
    "alerts-topic":       {"Team": "infra",         "Environment": "prod", "Owner": "frank"},

    # Équipe security
    "logs-archive":       {"Team": "security",      "Environment": "prod", "Owner": "grace"},
    "audit-logs":         {"Team": "security",      "Environment": "prod", "Owner": "grace"},

    # vol-orphan-*, eip-unused-*, i-0zombie999 → PAS de tags (détection FinOps)
}


def _base_cost(service: str, operation: str) -> float:
    """Retourne un coût journalier de base réaliste pour chaque combinaison service/opération."""
    # EC2 — dépend du type d'instance
    if service == "AmazonEC2":
        if "t3.xlarge" in operation:       return random.uniform(3.50, 5.00)
        if "m5.xlarge" in operation:       return random.uniform(3.00, 4.50)
        if "t3.large" in operation:        return random.uniform(1.80, 2.50)
        if "t3.medium" in operation:       return random.uniform(0.80, 1.20)
        if "t3.small" in operation:        return random.uniform(0.40, 0.60)
        if "t3.micro" in operation:        return random.uniform(0.15, 0.25)
        if "NatGateway" in operation:      return random.uniform(1.00, 1.50)
        if "DataTransfer" in operation:    return random.uniform(0.30, 0.80)
        return random.uniform(0.50, 1.00)

    # RDS
    if service == "AmazonRDS":
        if "t3.medium" in operation:       return random.uniform(2.00, 2.80)
        if "t3.small" in operation:        return random.uniform(1.00, 1.50)
        return random.uniform(1.50, 2.50)

    # Stockage
    if service == "AmazonS3":
        if "StorageStandard" in operation: return random.uniform(1.50, 2.50)  # Go stockés
        if "PutObject" in operation:       return random.uniform(0.05, 0.30)
        if "GetObject" in operation:       return random.uniform(0.10, 0.40)
        return random.uniform(0.10, 0.50)

    if service == "AmazonEBS":
        return random.uniform(0.15, 0.35)   # gp3 ~$0.10/Go/mois — orphelin assume 50-100Go

    # Services serverless
    if service == "AWSLambda":             return random.uniform(0.02, 0.30)
    if service == "AmazonDynamoDB":        return random.uniform(0.10, 0.50)
    if service == "AmazonAPIGateway":      return random.uniform(0.10, 0.40)
    if service == "AmazonSQS":             return random.uniform(0.01, 0.05)
    if service == "AmazonSNS":             return random.uniform(0.01, 0.03)

    # Réseau & CDN
    if service == "ElasticLoadBalancing":  return random.uniform(0.55, 0.85)
    if service == "AmazonCloudFront":      return random.uniform(0.80, 2.00)
    if service == "AmazonElastiCache":     return random.uniform(0.25, 0.45)

    # Monitoring
    if service == "AmazonCloudWatch":      return random.uniform(0.15, 0.40)

    # EIP idle = $0.005/h ≈ $0.12/jour
    if service == "AmazonEIP":             return random.uniform(0.10, 0.14)

    return random.uniform(0.05, 0.30)


def generate_cur_data(start: datetime, days: int, month_multiplier: float = 1.0, spike_days: set[int] | None = None) -> pd.DataFrame:
    """
    Génère des données CUR simulées pour N jours à partir d'une date.

    Args:
        start: Date de départ
        days: Nombre de jours à générer
        month_multiplier: Facteur global (ex: 1.15 = croissance de 15% vs mois précédent)
        spike_days: Indices de jours (0..N-1) où appliquer un pic de coût
    """
    rows = []
    spike_days = spike_days or set()

    for day_offset in range(days):
        current_date = start + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")

        # Multiplicateur global du jour : usage réduit le weekend, pic les jours spike
        is_weekend = current_date.weekday() >= 5
        is_spike = day_offset in spike_days

        if is_spike:
            day_multiplier = random.uniform(1.8, 2.3)  # +80-130% → détecté comme anomalie
        elif is_weekend:
            day_multiplier = random.uniform(0.7, 0.85)
        else:
            day_multiplier = random.uniform(0.95, 1.10)

        for service, operation, resource_id in SERVICES:
            base = _base_cost(service, operation)
            # Bruit + variation journalière + croissance mensuelle
            cost = round(base * random.uniform(0.85, 1.15) * day_multiplier * month_multiplier, 6)

            tags = TAGS.get(resource_id, {})

            rows.append({
                "line_item_usage_start_date": date_str,
                "line_item_product_code": service,
                "line_item_operation": operation,
                "line_item_resource_id": resource_id,
                "line_item_usage_amount": round(random.uniform(1, 24), 2),
                "line_item_unblended_cost": cost,
                "line_item_currency_code": "USD",
                "resource_tags_user_team": tags.get("Team", ""),
                "resource_tags_user_environment": tags.get("Environment", ""),
                "resource_tags_user_owner": tags.get("Owner", ""),
            })

    return pd.DataFrame(rows)


def generate_multi_month() -> pd.DataFrame:
    """Génère plusieurs mois de données pour simuler une évolution dans le temps."""
    # Mars 2026 — mois de référence (base 1.0), 2 pics
    march = generate_cur_data(
        start=datetime(2026, 3, 1),
        days=31,
        month_multiplier=1.0,
        spike_days={12, 22},  # 12 mars + 22 mars
    )

    # Avril 2026 — croissance (+12%) + plusieurs pics répartis dans le mois
    # Simule une équipe qui scale + incidents à investiguer
    april = generate_cur_data(
        start=datetime(2026, 4, 1),
        days=30,
        month_multiplier=1.12,       # +12% vs mars
        spike_days={4, 10, 16, 23},  # 5, 11, 17, 24 avril → 4 anomalies détectables
    )

    return pd.concat([march, april], ignore_index=True)


if __name__ == "__main__":
    print("Generating sample CUR data (2 mois : mars + avril 2026)...")
    df = generate_multi_month()

    # Sauvegarder en Parquet (comme le vrai CUR)
    output_path = "tests/fixtures/sample_cur.parquet"
    import os
    os.makedirs("tests/fixtures", exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"Generated {len(df)} rows → {output_path}")
    print(f"\nTotal global : ${df['line_item_unblended_cost'].sum():.2f}")
    print(f"Services : {df['line_item_product_code'].nunique()}")
    print(f"Ressources : {df['line_item_resource_id'].nunique()}")

    # Stats par mois
    df["month"] = pd.to_datetime(df["line_item_usage_start_date"]).dt.strftime("%Y-%m")
    month_totals = df.groupby("month")["line_item_unblended_cost"].sum()
    print("\nCoût par mois :")
    for month, cost in month_totals.items():
        print(f"  {month} : ${cost:.2f}")

    # Évolution mars → avril
    if "2026-03" in month_totals and "2026-04" in month_totals:
        diff = month_totals["2026-04"] - month_totals["2026-03"]
        pct = (diff / month_totals["2026-03"]) * 100
        print(f"  Évolution : {pct:+.1f}% (${diff:+.2f})")

    # Stats par équipe (sur les 2 mois)
    df_clean = df.drop(columns=["month"])
    team_totals = df_clean.groupby("resource_tags_user_team")["line_item_unblended_cost"].sum().sort_values(ascending=False)
    print("\nRépartition par équipe (2 mois) :")
    for team, cost in team_totals.items():
        name = team if team else "(untagged)"
        print(f"  {name:20s} ${cost:8.2f}")
