# tests/test_ingestion.py
# Tests unitaires pour la Lambda d'ingestion.
# Utilise moto pour simuler S3 et DynamoDB sans toucher à AWS.

import pytest
import boto3
from moto import mock_aws
from decimal import Decimal

from lambdas.ingestion.parser import parse_cur_from_s3, parse_cur_from_file
from lambdas.ingestion.enricher import (
    compute_daily_totals,
    compute_service_costs,
    compute_tag_costs,
    enrich_all,
)
from lambdas.ingestion.storage import write_items_to_dynamodb


# ---------------------------------------------------------------
# Fixtures pytest — se lancent avant chaque test qui les utilise
# ---------------------------------------------------------------

@pytest.fixture
def sample_df():
    """Charge le DataFrame de sample CUR pour les tests."""
    return parse_cur_from_file("tests/fixtures/sample_cur.parquet")


@pytest.fixture
def mock_s3_with_cur():
    """
    Crée un faux S3 avec le fichier CUR dedans.
    mock_aws() intercepte tous les appels boto3 et les redirige
    vers un simulateur en mémoire. Aucun appel réel à AWS.
    """
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-3")
        s3.create_bucket(
            Bucket="test-cur-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-3"}
        )
        # Upload le sample CUR dans le faux S3
        with open("tests/fixtures/sample_cur.parquet", "rb") as f:
            s3.put_object(Bucket="test-cur-bucket", Key="cur/sample.parquet", Body=f.read())
        yield s3


@pytest.fixture
def mock_dynamodb():
    """Crée une fausse table DynamoDB pour les tests."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-3")
        dynamodb.create_table(
            TableName="test-costs",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield dynamodb


# ---------------------------------------------------------------
# Tests du Parser
# ---------------------------------------------------------------

class TestParser:
    def test_parse_from_file_returns_dataframe(self, sample_df):
        """Le parser retourne un DataFrame non vide."""
        assert len(sample_df) > 0

    def test_parse_from_file_has_correct_columns(self, sample_df):
        """Le DataFrame contient exactement les colonnes attendues."""
        expected = [
            "line_item_usage_start_date",
            "line_item_product_code",
            "line_item_resource_id",
            "line_item_unblended_cost",
        ]
        for col in expected:
            assert col in sample_df.columns

    def test_parse_from_file_no_zero_costs(self, sample_df):
        """Aucune ligne avec un coût de 0 (filtrées par le parser)."""
        assert (sample_df["line_item_unblended_cost"] > 0).all()

    def test_parse_from_file_tags_filled(self, sample_df):
        """Les tags vides sont remplacés par 'untagged'."""
        assert "" not in sample_df["resource_tags_user_team"].values

    def test_parse_from_s3(self, mock_s3_with_cur):
        """Le parser peut lire depuis un faux S3."""
        df = parse_cur_from_s3(mock_s3_with_cur, "test-cur-bucket", "cur/sample.parquet")
        assert len(df) > 0
        assert "line_item_unblended_cost" in df.columns


# ---------------------------------------------------------------
# Tests de l'Enricher
# ---------------------------------------------------------------

class TestEnricher:
    def test_daily_totals_count(self, sample_df):
        """Un total par jour = 30 items pour 30 jours de données."""
        items = compute_daily_totals(sample_df)
        assert len(items) == 30

    def test_daily_totals_structure(self, sample_df):
        """Chaque item a la bonne structure PK/SK."""
        items = compute_daily_totals(sample_df)
        item = items[0]
        assert item["PK"].startswith("DAILY#")
        assert "totalCost" in item
        assert "expireAt" in item

    def test_service_costs_has_items(self, sample_df):
        """Il y a des coûts par service."""
        items = compute_service_costs(sample_df)
        assert len(items) > 0

    def test_tag_costs_has_untagged(self, sample_df):
        """Les ressources sans tags génèrent un coût 'untagged'."""
        items = compute_tag_costs(sample_df)
        teams = [i["team"] for i in items]
        assert "untagged" in teams

    def test_enrich_all_combines(self, sample_df):
        """enrich_all retourne la somme de toutes les agrégations."""
        items = enrich_all(sample_df)
        daily = compute_daily_totals(sample_df)
        services = compute_service_costs(sample_df)
        tags = compute_tag_costs(sample_df)
        assert len(items) == len(daily) + len(services) + len(tags)


# ---------------------------------------------------------------
# Tests du Storage
# ---------------------------------------------------------------

class TestStorage:
    def test_write_items(self, mock_dynamodb):
        """Écrire des items dans DynamoDB et les relire."""
        items = [
            {"PK": "DAILY#2026-03", "SK": "2026-03-01", "totalCost": 12.45},
            {"PK": "DAILY#2026-03", "SK": "2026-03-02", "totalCost": 11.20},
        ]
        written = write_items_to_dynamodb(mock_dynamodb, "test-costs", items)
        assert written == 2

        # Relire pour vérifier
        table = mock_dynamodb.Table("test-costs")
        response = table.get_item(Key={"PK": "DAILY#2026-03", "SK": "2026-03-01"})
        assert "Item" in response
        assert response["Item"]["totalCost"] == Decimal("12.45")
