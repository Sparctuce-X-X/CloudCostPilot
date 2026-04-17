# CloudCostPilot

Outil FinOps serverless sur AWS pour analyser, optimiser et alerter sur les coûts cloud.

## Objectif

Ingérer automatiquement les AWS Cost & Usage Reports, détecter les gaspillages (EBS orphelins, EC2 surprovisionnées, NAT Gateway sous-utilisées...), et exposer les résultats via un dashboard interactif.

## Architecture

```
AWS Cost & Usage Reports (Parquet)
        │
        ▼
   S3 (stockage CUR)
        │
        ▼ (trigger S3 → Lambda)
   Lambda Ingestion (Python)
        │
        ▼
   DynamoDB (données enrichies)
        │
        ├──▶ Lambda Detective (règles de détection)
        │         │
        │         ▼
        │    SNS (alertes email + Slack)
        │
        ▼
   API Gateway (REST)
        │
        ▼
   Dashboard Next.js (Vercel)
```

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Infrastructure as Code | Terraform |
| Ingestion & détection | AWS Lambda (Python 3.11) |
| Stockage brut | Amazon S3 |
| Stockage enrichi | Amazon DynamoDB |
| API | Amazon API Gateway (HTTP API) |
| Scheduling | Amazon EventBridge |
| Alerting | Amazon SNS |
| Dashboard | Next.js / TypeScript / Tailwind / Recharts |
| Hébergement frontend | Vercel |
| CI/CD | GitHub Actions |
| Sécurité | checkov (Terraform) + bandit (Python) |
| Tests | pytest + moto |

## Structure du projet

```
CloudCostPilot/
├── infra/                # Terraform (IaC)
├── lambdas/
│   ├── ingestion/        # Lambda de parsing CUR
│   └── detection/        # Lambda de détection de gaspillages
├── api/                  # Handlers API Gateway
├── frontend/             # Dashboard Next.js (Phase 4)
├── tests/                # Tests pytest
├── docs/                 # Documentation, schémas
├── .github/workflows/    # CI/CD GitHub Actions
├── LEARNING.md           # Journal d'apprentissage
└── README.md
```

## Avancement

- [x] Phase 0 — Setup environnement (outils, AWS, CUR)
- [x] Phase 1 — Infrastructure Terraform (S3, DynamoDB, IAM, remote state)
- [x] Phase 2 — Lambda d'ingestion (parser, enricher, storage, 11 tests, déployée)
- [x] Phase 3 — Détection + API (4 règles FinOps, 6 endpoints REST, alertes SNS)
- [x] Phase 4 — Dashboard Next.js (4 pages, Recharts, déploiement Vercel en cours)
- [ ] Phase 5 — CI/CD + polish (GitHub Actions en place, fiches entretien restantes)

## Coût estimé

Projet conçu pour rester sous **$5** en usage normal grâce au Free Tier AWS et au mode on-demand sur DynamoDB. Alertes de facturation configurées à $5, $10 et $15.

## Auteur

**Dominique Huang** — Développeur full-stack en alternance, passionné DevOps/Cloud.
