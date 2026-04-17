# lambdas/detection/rules.py
# Règles de détection de gaspillages AWS.
# Chaque règle est une fonction pure : entrée → liste de recommandations.
# Ça les rend testables individuellement.

from typing import Any
from datetime import datetime, timedelta
from decimal import Decimal


def detect_untagged_resources(cost_items: list[dict]) -> list[dict[str, Any]]:
    """
    Détecte les ressources qui ont un coût mais pas de tag "team".
    En FinOps, une ressource non taggée = impossible à attribuer à une équipe.
    C'est souvent le signe d'une ressource oubliée.

    Args:
        cost_items: Items DynamoDB de type service costs (PK=DAILY#date, SK=service)

    Returns:
        Liste de recommandations à stocker dans DynamoDB.
    """
    # On cherche les items du tag "untagged" dans les données
    recommendations = []
    untagged_costs = {}

    for item in cost_items:
        sk = item.get("SK", "")
        if "untagged" in sk:
            team = item.get("team", "untagged")
            cost = float(item.get("totalCost", 0))
            date = item.get("date", "")

            if team == "untagged":
                # Accumuler le coût total des ressources non taggées
                untagged_costs[date] = untagged_costs.get(date, 0) + cost

    if untagged_costs:
        total_untagged = sum(untagged_costs.values())
        recommendations.append({
            "PK": "RECOMMENDATION",
            "SK": f"untagged-resources#{datetime.now().strftime('%Y-%m-%d')}",
            "type": "untagged-resources",
            "severity": "medium",
            "title": "Ressources sans tags détectées",
            "description": f"{len(untagged_costs)} jours avec des coûts non taggés. "
                          f"Total: ${total_untagged:.2f}. "
                          f"Ajoutez des tags Team/Owner pour l'attribution.",
            "estimatedWaste": Decimal(str(round(total_untagged, 2))),
            "detectedAt": datetime.now().isoformat(),
            "status": "open",
            "expireAt": int((datetime.now() + timedelta(days=90)).timestamp()),
        })

    return recommendations


def detect_cost_anomalies(daily_items: list[dict]) -> list[dict[str, Any]]:
    """
    Détecte les anomalies de coût : un jour qui coûte >50% de plus que la moyenne.
    C'est un algorithme simple mais efficace pour les petits comptes.

    En entreprise, on utiliserait CloudWatch Anomaly Detection ou un modèle ML.
    Ici on fait une détection par seuil — parfait pour commencer.
    """
    if len(daily_items) < 7:
        return []  # Pas assez de données pour calculer une moyenne fiable

    # Extraire les coûts par jour
    daily_costs = []
    for item in daily_items:
        cost = float(item.get("totalCost", 0))
        date = item.get("SK", "")
        if cost > 0 and date:
            daily_costs.append({"date": date, "cost": cost})

    if len(daily_costs) < 7:
        return []

    # Trier par date
    daily_costs.sort(key=lambda x: x["date"])

    # Calculer la moyenne mobile sur les 7 derniers jours
    recommendations = []
    for i in range(7, len(daily_costs)):
        window = daily_costs[i-7:i]
        avg = sum(d["cost"] for d in window) / len(window)
        current = daily_costs[i]

        # Si le coût du jour dépasse 150% de la moyenne → anomalie
        if avg > 0 and current["cost"] > avg * 1.5:
            spike_pct = ((current["cost"] - avg) / avg) * 100
            recommendations.append({
                "PK": "ANOMALY#" + current["date"][:7],
                "SK": f"{current['date']}#cost-spike",
                "type": "cost-spike",
                "severity": "high",
                "title": f"Pic de coût le {current['date']}",
                "description": f"Coût de ${current['cost']:.2f} vs moyenne "
                              f"${avg:.2f} (+{spike_pct:.0f}%). "
                              f"Vérifiez les services actifs ce jour.",
                "dailyCost": Decimal(str(round(current["cost"], 2))),
                "averageCost": Decimal(str(round(avg, 2))),
                "spikePct": Decimal(str(round(spike_pct, 1))),
                "detectedAt": datetime.now().isoformat(),
                "status": "open",
                "expireAt": int((datetime.now() + timedelta(days=90)).timestamp()),
            })

    return recommendations


def detect_ebs_orphans(ec2_client) -> list[dict[str, Any]]:
    """
    Détecte les volumes EBS non attachés à une instance EC2.
    Un volume "available" = il existe mais n'est branché à rien.
    → Tu paies le stockage pour rien.

    Coût : $0.10/Go/mois en gp3 (eu-west-3).
    Un volume de 100Go oublié = $10/mois pour rien.
    """
    recommendations = []

    volumes = ec2_client.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )

    for vol in volumes.get("Volumes", []):
        vol_id = vol["VolumeId"]
        size_gb = vol["Size"]
        monthly_cost = size_gb * 0.10  # gp3 pricing eu-west-3

        recommendations.append({
            "PK": "RECOMMENDATION",
            "SK": f"ebs-orphan#{vol_id}",
            "type": "ebs-orphan",
            "severity": "high" if monthly_cost > 5 else "medium",
            "title": f"Volume EBS orphelin: {vol_id}",
            "description": f"Volume de {size_gb} Go non attaché. "
                          f"Coût: ${monthly_cost:.2f}/mois. "
                          f"Supprimez-le ou attachez-le à une instance.",
            "resourceId": vol_id,
            "sizeGb": size_gb,
            "estimatedWaste": Decimal(str(round(monthly_cost, 2))),
            "detectedAt": datetime.now().isoformat(),
            "status": "open",
            "expireAt": int((datetime.now() + timedelta(days=90)).timestamp()),
        })

    return recommendations


def detect_unused_eips(ec2_client) -> list[dict[str, Any]]:
    """
    Détecte les Elastic IPs non associées à une instance.
    AWS facture $3.60/mois pour une EIP non utilisée (depuis fév 2024).
    Avant c'était gratuit si associée — maintenant c'est payant dans tous les cas,
    mais une EIP non associée coûte PLUS cher.
    """
    recommendations = []

    addresses = ec2_client.describe_addresses()

    for eip in addresses.get("Addresses", []):
        # Si pas de InstanceId ni de NetworkInterfaceId → non utilisée
        if "InstanceId" not in eip and "NetworkInterfaceId" not in eip:
            alloc_id = eip.get("AllocationId", "unknown")
            public_ip = eip.get("PublicIp", "unknown")

            recommendations.append({
                "PK": "RECOMMENDATION",
                "SK": f"eip-unused#{alloc_id}",
                "type": "eip-unused",
                "severity": "medium",
                "title": f"Elastic IP non utilisée: {public_ip}",
                "description": f"EIP {public_ip} ({alloc_id}) n'est associée "
                              f"à aucune instance. Coût: $3.60/mois. "
                              f"Libérez-la si vous n'en avez plus besoin.",
                "resourceId": alloc_id,
                "publicIp": public_ip,
                "estimatedWaste": Decimal("3.60"),
                "detectedAt": datetime.now().isoformat(),
                "status": "open",
                "expireAt": int((datetime.now() + timedelta(days=90)).timestamp()),
            })

    return recommendations
