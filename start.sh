#!/bin/bash
set -e

echo "Démarrage du pipeline..."

# Exécuter les commandes en séquence
python ./data/fetch_data.py
python -m model.pipeline.PipelineOrchestrator
python -m model.pipeline.PipelineBatchPredictor
