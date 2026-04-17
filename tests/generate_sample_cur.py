# tests/generate_sample_cur.py
# Génère un fichier CUR (Cost & Usage Report) fictif au format Parquet.
# Ce fichier sert pour le développement et les tests, sans attendre le vrai CUR d'AWS.

import pandas as pd
from datetime import datetime, timedelta
import random

# ---------------------------------------------------------------
# Colonnes du CUR qu'on va utiliser dans notre projet.
# Le vrai CUR a 50+ colonnes — on simule les 10 essentielles.
# ---------------------------------------------------------------

# Services AWS réalistes avec leurs opérations typiques
SERVICES = [
    ("AmazonEC2", "RunInstances", "i-0abc123def456"),
    ("AmazonEC2", "RunInstances", "i-0def789ghi012"),
    ("AmazonEC2", "NatGateway", "nat-0aaa111bbb222"),
    ("AmazonS3", "PutObject", "my-app-bucket"),
    ("AmazonS3", "GetObject", "my-app-bucket"),
    ("AmazonDynamoDB", "PayPerRequestThroughput", "users-table"),
    ("AWSLambda", "Invoke", "process-orders"),
    ("AWSLambda", "Invoke", "send-notifications"),
    ("AmazonCloudWatch", "PutLogEvents", ""),
    ("AmazonRDS", "CreateDBInstance", "db-prod-postgres"),
    ("ElasticLoadBalancing", "LoadBalancerUsage", "app-alb"),
    ("AmazonEBS", "VolumeUsage", "vol-orphan-001"),     # EBS orphelin — pas attaché
    ("AmazonEIP", "ElasticIP:IdleAddress", "eip-unused-001"),  # EIP non utilisée
]

# Tags simulés (certaines ressources n'ont PAS de tags — c'est voulu pour la détection)
TAGS = {
    "i-0abc123def456": {"Team": "backend", "Environment": "prod", "Owner": "alice"},
    "i-0def789ghi012": {"Team": "data", "Environment": "dev", "Owner": "bob"},
    "nat-0aaa111bbb222": {"Team": "infra", "Environment": "prod"},
    "my-app-bucket": {"Team": "backend", "Environment": "prod"},
    "users-table": {"Team": "backend", "Environment": "prod"},
    "process-orders": {"Team": "backend", "Environment": "prod"},
    "send-notifications": {"Team": "backend", "Environment": "prod"},
    "db-prod-postgres": {"Team": "data", "Environment": "prod", "Owner": "bob"},
    "app-alb": {"Team": "infra", "Environment": "prod"},
    # vol-orphan-001 et eip-unused-001 n'ont PAS de tags → suspect
}


def generate_cur_data(days: int = 30) -> pd.DataFrame:
    """Génère des données CUR simulées pour N jours."""
    rows = []
    start_date = datetime(2026, 3, 1)

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")

        for service, operation, resource_id in SERVICES:
            # Coût journalier réaliste par service
            if service == "AmazonEC2" and "RunInstances" in operation:
                base_cost = random.uniform(1.50, 4.00)      # EC2 = le plus cher
            elif service == "AmazonRDS":
                base_cost = random.uniform(2.00, 3.50)       # RDS = cher aussi
            elif service == "AmazonEC2" and "NatGateway" in operation:
                base_cost = random.uniform(0.80, 1.50)       # NAT = coûteux pour le trafic
            elif service == "ElasticLoadBalancing":
                base_cost = random.uniform(0.50, 0.80)
            elif service == "AmazonEBS":
                base_cost = random.uniform(0.10, 0.30)       # EBS orphelin
            elif service == "AmazonEIP":
                base_cost = random.uniform(0.005, 0.01)      # EIP idle = $0.005/h
            else:
                base_cost = random.uniform(0.01, 0.50)

            # Ajouter du bruit pour simuler des variations réalistes
            cost = round(base_cost * random.uniform(0.8, 1.2), 6)

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


if __name__ == "__main__":
    print("Generating sample CUR data...")
    df = generate_cur_data(days=30)

    # Sauvegarder en Parquet (comme le vrai CUR)
    output_path = "tests/fixtures/sample_cur.parquet"
    import os
    os.makedirs("tests/fixtures", exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"Generated {len(df)} rows → {output_path}")
    print("\nAperçu:")
    print(df.head(10).to_string())
    print(f"\nCoût total simulé: ${df['line_item_unblended_cost'].sum():.2f}")
    print(f"Services: {df['line_item_product_code'].nunique()}")
    print(f"Ressources: {df['line_item_resource_id'].nunique()}")
