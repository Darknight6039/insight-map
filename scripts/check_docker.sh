#!/bin/bash

echo "🐳 Vérification de l'installation Docker"
echo "======================================="

# Vérifier Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker installé"
    docker --version
else
    echo "❌ Docker non trouvé"
    echo "Installez Docker Desktop depuis : https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Vérifier Docker Compose (nouvelle syntaxe)
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose disponible (nouvelle syntaxe)"
    docker compose version
elif docker-compose --version &> /dev/null; then
    echo "✅ Docker Compose disponible (ancienne syntaxe)"
    docker-compose --version
else
    echo "❌ Docker Compose non trouvé"
    exit 1
fi

# Vérifier que Docker daemon tourne
if docker info &> /dev/null; then
    echo "✅ Docker daemon en cours d'exécution"
else
    echo "❌ Docker daemon non démarré"
    echo "Lancez Docker Desktop depuis Applications"
    exit 1
fi

echo ""
echo "🎉 Docker est prêt ! Vous pouvez maintenant lancer :"
echo "docker compose up -d --build"
