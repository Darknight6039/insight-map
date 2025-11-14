FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY report-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copier le code de l'application
COPY report-service/app /app/app

# Copier le dossier filigrane depuis la racine du projet
COPY filigrane /app/filigrane

# Copier le dossier templates (optionnel)
COPY templates /app/templates

EXPOSE 8004
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]


