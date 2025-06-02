# Choisir une image de base officielle Python
FROM python:3.11

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

COPY ..requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY api .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]