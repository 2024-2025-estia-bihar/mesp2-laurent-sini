# MESP2 Laurent SINI
High-level description

Data flow & architecture


Charge les données brute de l'API open-meteo
```bash
py .\data\fetch_data.py
```

Execution du pipeline d'entrainement
```bash
py -m model.pipeline.PipelineOrchestrator
```

Execution du pipeline de prediction par approche batch
```bash
py -m model.pipeline.PipelineBatchPredictor
```

Main technologies used and for which purpose

# Running locally
Instructions to install dependencies, run, build, test

```bash
pip install -r requirements.txt
```

Lancement de l'API
```bash
uvicorn api.main:app --reload
```

Test localment l'API
```Bash
docker build -t my-api:local ./api
docker run -p 8080:8000 my-api:local
```

# CI/CD steps
Short description of each step with their outputs (if any)
