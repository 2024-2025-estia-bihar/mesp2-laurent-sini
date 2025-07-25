# Choisir une image de base officielle Python
FROM python:3.12

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

ARG API_VERSION=0.0.0
RUN echo "${API_VERSION}" > /app/version.txt

ENV APP_ENV='dev'
ENV POSTGRES_HOST='db'
ENV POSTGRES_DB='mesp'

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api api
COPY model model

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]