# CloudCostPilot — Workflow complet

> Roadmap exhaustive du projet, de zéro jusqu'au projet fonctionnel et déployé.
> Chaque case à cocher = une étape concrète. On avance linéairement, en mode apprentissage.

**Budget AWS max : $15** · **Stack : Terraform + Python + Next.js + GitHub Actions**

---

## PHASE 0 — Setup de l'environnement (1-2h)

### 0.1 — Outils locaux

- [ ] **Homebrew** installé (✅ déjà OK — v5.1.1)
- [ ] **Python 3.11** installé via `brew install python@3.11`
- [ ] **AWS CLI v2** installé via `brew install awscli`
- [ ] **Terraform** installé via `brew install terraform`
- [ ] **jq** (parseur JSON en CLI) installé via `brew install jq`
- [ ] **Vérification finale** : `python3.11 --version`, `aws --version`, `terraform --version`, `jq --version`

**Concepts abordés** : gestionnaire de paquets, versions runtime AWS Lambda, pourquoi ne pas modifier le Python système.

### 0.2 — Compte AWS sécurisé

- [ ] Créer un compte AWS (ou utiliser celui existant)
- [ ] Activer **MFA sur le compte root** (OBLIGATOIRE, sinon risque de compromission)
- [ ] Créer un utilisateur IAM dédié `cloudcostpilot-admin` (on ne travaille JAMAIS en root)
- [ ] Activer MFA sur cet utilisateur IAM
- [ ] Générer les **Access Keys** pour cet utilisateur
- [ ] Configurer une **alerte de facturation à $5, $10, $15** (AWS Budgets)
- [ ] Activer les **tags de coûts** dans Cost Management → Cost allocation tags

**Concepts abordés** : principe du moindre privilège, différence root/IAM user, AWS Organizations (brièvement), billing alarms.

### 0.3 — Configuration AWS CLI locale

- [ ] `aws configure --profile cloudcostpilot` avec les Access Keys
- [ ] Vérifier l'identité : `aws sts get-caller-identity --profile cloudcostpilot`
- [ ] Ajouter `export AWS_PROFILE=cloudcostpilot` dans `~/.zshrc`

**Concepts abordés** : profils AWS CLI, variables d'environnement, STS.

### 0.4 — Repo GitHub

- [ ] Initialiser le repo Git local (déjà fait — on est dessus)
- [ ] Créer la structure de dossiers :
  ```
  CloudCostPilot/
  ├── infra/              # Terraform
  ├── lambdas/            # Code Python des Lambdas
  │   ├── ingestion/
  │   └── detection/
  ├── api/                # API Gateway handlers
  ├── frontend/           # Next.js dashboard (Phase 4)
  ├── tests/              # Tests pytest
  ├── .github/workflows/  # CI/CD
  ├── docs/               # Schémas, captures
  ├── LEARNING.md         # Journal d'apprentissage
  ├── WORKFLOW.md         # Ce fichier
  └── README.md
  ```
- [ ] `.gitignore` correct (venv, .terraform, *.tfstate, .env, __pycache__, node_modules)
- [ ] Créer un repo GitHub public `cloudcostpilot` et push initial
- [ ] Créer `LEARNING.md` (journal de bord)

**Concepts abordés** : structure monorepo, .gitignore critique pour ne JAMAIS commit de secrets ou de tfstate.

### 0.5 — Configuration CUR dans AWS

- [ ] Créer un bucket S3 `cloudcostpilot-cur-reports-<account-id>` (nommage unique globalement)
- [ ] Configurer un **Cost & Usage Report** dans Billing → Data Exports
- [ ] Format : **Parquet**, niveau horaire, avec **resource IDs** + **tags**
- [ ] Attendre 24h pour avoir le premier fichier CUR

**Concepts abordés** : CUR 2.0, format Parquet, policy bucket pour AWS Billing Service.

### 0.6 — Environnement Python local

- [ ] Créer un venv : `python3.11 -m venv .venv`
- [ ] Activer : `source .venv/bin/activate`
- [ ] Installer les deps de base : `pip install boto3 pandas pyarrow pytest moto ruff`
- [ ] Créer `requirements.txt` et `requirements-dev.txt`

**Concepts abordés** : virtualenv, séparation deps runtime vs dev, pinning de versions.

---

## PHASE 1 — Infrastructure Terraform (4-5h)

### 1.1 — Comprendre Terraform (théorie)

- [ ] Cours : providers, resources, data sources, variables, outputs
- [ ] Cours : le state file, pourquoi il est critique
- [ ] Cours : `plan` vs `apply` vs `destroy`

### 1.2 — Premier module Terraform : backend distant

- [ ] Créer manuellement (via AWS Console ou CLI) un bucket S3 `cloudcostpilot-tfstate-<account-id>` pour stocker le state
- [ ] Créer manuellement une table DynamoDB `cloudcostpilot-tflock` pour le state locking
- [ ] Écrire `infra/backend.tf` avec la config du remote state
- [ ] `terraform init` → vérifier que le backend est bien configuré

**Concepts abordés** : pourquoi un state distant, state locking (éviter les conflits en équipe), poule-et-œuf du bootstrap Terraform.

### 1.3 — Bucket S3 pour les Lambdas artifacts

- [ ] Écrire `infra/s3.tf` : bucket pour les .zip des Lambdas
- [ ] Versioning activé
- [ ] Block public access
- [ ] `terraform plan` puis `terraform apply`

### 1.4 — Table DynamoDB pour les coûts

- [ ] Écrire `infra/dynamodb.tf` : table `costs` avec PK/SK bien choisies
- [ ] Mode **on-demand** (PAY_PER_REQUEST) — pas de provisionnement
- [ ] TTL pour purger les vieilles données
- [ ] Réflexion sur le **modèle de données** : single-table design ou plusieurs tables ?

**Concepts abordés** : NoSQL vs SQL, partitioning, hot partitions, single-table design (Rick Houlihan), coût DynamoDB.

### 1.5 — IAM Role pour Lambda

- [ ] Écrire `infra/iam.tf` : rôle assumable par Lambda
- [ ] Policy : lecture S3 CUR, écriture DynamoDB, CloudWatch Logs
- [ ] Appliquer le principe du moindre privilège

**Concepts abordés** : trust policy vs permission policy, assume role, least privilege.

### 1.6 — Premier destroy propre

- [ ] `terraform destroy` pour valider qu'on peut détruire proprement
- [ ] Re-apply pour remettre en place

**⚠️ Important** : à partir d'ici, toujours `destroy` en fin de session tant que la stack n'est pas finalisée.

---

## PHASE 2 — Lambda d'ingestion (5-6h)

### 2.1 — Structure du code Python

- [ ] Architecture : `handler.py` → `parser.py` → `enricher.py` → `storage.py`
- [ ] Séparer la logique métier du handler (testabilité)
- [ ] Type hints partout (mypy ready)

**Concepts abordés** : clean architecture, ports & adapters, testabilité.

### 2.2 — Parsing du CUR

- [ ] Lire un fichier Parquet depuis S3 avec `pyarrow` ou `pandas`
- [ ] Filtrer les colonnes utiles (~10 sur 50+)
- [ ] Gérer le cas "gros fichier" (streaming avec `pyarrow.dataset`)

### 2.3 — Enrichissement

- [ ] Agrégation par service / par tag / par jour
- [ ] Calcul des métriques : coût total, coût par catégorie, évolution jour/jour

### 2.4 — Écriture DynamoDB

- [ ] `BatchWriter` pour l'efficacité (25 items par batch)
- [ ] Gestion des throttles (exponential backoff)
- [ ] Idempotence (rejouer l'ingestion ne doit pas doubler les données)

### 2.5 — Tests unitaires

- [ ] Setup pytest
- [ ] Mock AWS avec **moto**
- [ ] Tests parser, enricher, storage
- [ ] Fixture CUR sample (petit fichier Parquet de test)

**Concepts abordés** : pytest fixtures, mocking, idempotence.

### 2.6 — Packaging et déploiement

- [ ] Script de build : `make build` qui crée le `.zip`
- [ ] Terraform : `aws_lambda_function` avec trigger S3 PutObject
- [ ] `terraform apply` + test manuel en déposant un fichier dans S3
- [ ] Vérifier les logs CloudWatch

**Concepts abordés** : packaging Lambda, layers vs zip, cold start, triggers event-driven.

---

## PHASE 3 — Détection + API (4-5h)

### 3.1 — Lambda "detective"

- [ ] Règles de détection :
  - EBS volumes non attachés > 7 jours
  - Elastic IPs non associées
  - NAT Gateway avec faible trafic
  - EC2 sous-utilisées (CPU moyen < 10%)
  - Buckets S3 sans lifecycle policy
- [ ] Chaque règle = une fonction pure, testable

### 3.2 — API Gateway + Lambda handlers

- [ ] Endpoints :
  - `GET /costs?from=&to=&groupBy=`
  - `GET /recommendations`
  - `GET /anomalies`
- [ ] Structure JSON de réponse consistante
- [ ] Gestion des erreurs HTTP propres

**Concepts abordés** : REST design, API Gateway REST vs HTTP API (on prendra HTTP API = moins cher), CORS.

### 3.3 — Scheduler EventBridge

- [ ] Rule EventBridge qui déclenche la Lambda detective tous les matins
- [ ] Cron expression

### 3.4 — Alertes SNS

- [ ] Topic SNS `cost-anomalies`
- [ ] Subscription email + Slack webhook
- [ ] Lambda detective publie sur le topic si anomalie détectée

**Concepts abordés** : pub/sub, fan-out, webhooks Slack.

---

## PHASE 4 — Dashboard Next.js (3-4h)

### 4.1 — Setup projet

- [ ] `npx create-next-app@latest frontend --typescript --tailwind --app`
- [ ] Variables d'env pour l'URL API
- [ ] Auth simple (API key header)

### 4.2 — Pages et composants

- [ ] `/` — Vue d'ensemble coûts du mois
- [ ] `/recommendations` — Liste des gaspillages détectés
- [ ] `/anomalies` — Graphique temporel
- [ ] `/by-service` — Pie chart par service AWS
- [ ] `/by-tag` — Répartition par équipe/environnement

### 4.3 — Graphiques avec Recharts

- [ ] Line chart, bar chart, pie chart

### 4.4 — Déploiement Vercel

- [ ] Connecter le repo GitHub à Vercel
- [ ] Variables d'env configurées
- [ ] Preview deployments activés

---

## PHASE 5 — CI/CD + polish (2-3h)

### 5.1 — GitHub Actions

- [ ] Workflow `test.yml` : pytest + ruff à chaque PR
- [ ] Workflow `security.yml` : bandit (Python) + checkov (Terraform)
- [ ] Workflow `deploy.yml` : terraform apply sur push main (avec approval manuel)
- [ ] Secrets GitHub : AWS credentials via OIDC (PAS de long-lived keys)

**Concepts abordés** : OIDC federation GitHub → AWS, matrix builds, artifacts, environments GitHub.

### 5.2 — Documentation

- [ ] README complet avec :
  - Description du projet + contexte FinOps
  - Schéma d'architecture (Excalidraw ou Mermaid)
  - Instructions de déploiement
  - Captures du dashboard
  - Estimation détaillée des coûts
  - Vidéo Loom de démo (2-3 min)
- [ ] `docs/ARCHITECTURE.md`
- [ ] `docs/RUNBOOK.md` (procédures d'opération)

### 5.3 — Fiches de défense entretien

- [ ] Pour chaque phase, 3-5 questions pièges + réponses
- [ ] Stocké dans `docs/INTERVIEW_PREP.md`

---

## PHASE 6 — Au-delà (optionnel, si le temps)

- [ ] Multi-account : support de l'ingestion CUR depuis plusieurs comptes AWS (organisation)
- [ ] ML simple : détection d'anomalies avec `scikit-learn` ou CloudWatch Anomaly Detection
- [ ] Export recommandations au format PDF
- [ ] Compatibilité Azure Cost Management (multi-cloud)

---

## Règles durables du projet

1. **Toujours `terraform destroy` en fin de session** tant que la stack n'est pas finalisée
2. **Vérifier la facture AWS tous les 2-3 jours** via Cost Explorer
3. **Commiter souvent**, messages clairs (conventional commits)
4. **Mettre à jour `LEARNING.md` après chaque session**
5. **Ne jamais commiter** : `.env`, `*.tfstate`, access keys, `venv/`

---

## Checkpoint coût estimé par phase

| Phase | Ressources créées | Coût estimé si détruit en fin de session | Coût estimé si laissé 24h |
|-------|-------------------|------------------------------------------|---------------------------|
| 0 | CUR S3 bucket | $0 | ~$0.01 |
| 1 | S3 + DynamoDB on-demand + IAM | $0 | ~$0.02 |
| 2 | + Lambda + invocations | $0 | ~$0.10 |
| 3 | + API Gateway + EventBridge + SNS | $0 | ~$0.15 |
| 4 | + Vercel (gratuit) | $0 | $0 |
| 5 | CI/CD | $0 (GitHub Actions free tier) | $0 |

**Total projet si bien géré : < $5. Alerte placée à $15 pour marge de sécurité.**
