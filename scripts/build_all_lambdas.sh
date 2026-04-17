#!/bin/bash
# scripts/build_all_lambdas.sh
# Construit les .zip de toutes les Lambdas.

set -e

echo "=== Building all Lambdas ==="

# Lambda ingestion
rm -rf build/ingestion build/ingestion.zip
mkdir -p build/ingestion/lambdas/ingestion
cp lambdas/__init__.py build/ingestion/lambdas/
cp lambdas/ingestion/__init__.py build/ingestion/lambdas/ingestion/
cp lambdas/ingestion/handler.py lambdas/ingestion/parser.py lambdas/ingestion/enricher.py lambdas/ingestion/storage.py build/ingestion/lambdas/ingestion/
cd build/ingestion && zip -r ../ingestion.zip . -q && cd ../..
echo "  ingestion.zip ($(du -h build/ingestion.zip | cut -f1))"

# Lambda detection
rm -rf build/detection build/detection.zip
mkdir -p build/detection/lambdas/detection build/detection/lambdas/ingestion
cp lambdas/__init__.py build/detection/lambdas/
cp lambdas/detection/__init__.py build/detection/lambdas/detection/
cp lambdas/detection/handler.py lambdas/detection/rules.py build/detection/lambdas/detection/
# Detection réutilise storage.py de ingestion (pour écrire les recommandations)
cp lambdas/ingestion/__init__.py build/detection/lambdas/ingestion/
cp lambdas/ingestion/storage.py build/detection/lambdas/ingestion/
cd build/detection && zip -r ../detection.zip . -q && cd ../..
echo "  detection.zip ($(du -h build/detection.zip | cut -f1))"

# Lambda API
rm -rf build/api build/api.zip
mkdir -p build/api/api
cp api/handler.py build/api/api/
touch build/api/api/__init__.py
cd build/api && zip -r ../api.zip . -q && cd ../..
echo "  api.zip ($(du -h build/api.zip | cut -f1))"

echo "=== Done ==="
