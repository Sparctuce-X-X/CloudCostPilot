#!/bin/bash
# scripts/build_lambda.sh
# Crée le .zip de la Lambda d'ingestion pour le déploiement.
# Ne contient que le code — les dépendances (pandas, pyarrow) sont dans un Layer AWS.

set -e  # Arrête le script si une commande échoue

LAMBDA_NAME="ingestion"
BUILD_DIR="build/${LAMBDA_NAME}"
ZIP_FILE="build/${LAMBDA_NAME}.zip"

echo "=== Building Lambda: ${LAMBDA_NAME} ==="

# Nettoyer le build précédent
rm -rf "${BUILD_DIR}" "${ZIP_FILE}"
mkdir -p "${BUILD_DIR}/lambdas/ingestion"

# Copier le code source
cp lambdas/__init__.py "${BUILD_DIR}/lambdas/"
cp lambdas/ingestion/__init__.py "${BUILD_DIR}/lambdas/ingestion/"
cp lambdas/ingestion/handler.py "${BUILD_DIR}/lambdas/ingestion/"
cp lambdas/ingestion/parser.py "${BUILD_DIR}/lambdas/ingestion/"
cp lambdas/ingestion/enricher.py "${BUILD_DIR}/lambdas/ingestion/"
cp lambdas/ingestion/storage.py "${BUILD_DIR}/lambdas/ingestion/"

# Créer le .zip
cd "${BUILD_DIR}"
zip -r "../../${ZIP_FILE}" . -q

cd ../..
echo "=== Built: ${ZIP_FILE} ($(du -h ${ZIP_FILE} | cut -f1)) ==="
