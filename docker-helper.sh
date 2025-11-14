#!/bin/bash
# Helper script pour gérer l'application Axial Intelligence
# Utilise automatiquement le projet 'insight_mvp' avec les données originales

export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
cd "$(dirname "$0")"

case "$1" in
  start|up)
    echo "🚀 Démarrage de l'application Axial Intelligence..."
    docker compose up -d
    echo "✅ Application démarrée!"
    echo ""
    echo "📍 URLs disponibles:"
    echo "   - Frontend Open WebUI: http://localhost:3000"
    echo "   - Frontend Gradio: http://localhost:7860"
    echo "   - Gateway API: http://localhost:8000"
    echo "   - RAG Service: http://localhost:8003"
    echo "   - Backend Service: http://localhost:8006"
    ;;
    
  stop|down)
    echo "🛑 Arrêt de l'application..."
    docker compose down
    echo "✅ Application arrêtée!"
    ;;
    
  restart)
    echo "🔄 Redémarrage de l'application..."
    docker compose restart
    echo "✅ Application redémarrée!"
    ;;
    
  logs)
    if [ -z "$2" ]; then
      docker compose logs -f
    else
      docker compose logs -f "$2"
    fi
    ;;
    
  ps|status)
    echo "📊 État des services:"
    docker compose ps
    ;;
    
  rebuild)
    echo "🔨 Rebuild complet de l'application..."
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    echo "✅ Rebuild terminé!"
    ;;
    
  clean)
    echo "🧹 Nettoyage des containers arrêtés..."
    docker container prune -f
    echo "✅ Nettoyage terminé!"
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|logs [service]|status|rebuild|clean}"
    echo ""
    echo "Commandes disponibles:"
    echo "  start/up    - Démarrer l'application"
    echo "  stop/down   - Arrêter l'application"
    echo "  restart     - Redémarrer l'application"
    echo "  logs [svc]  - Voir les logs (optionnel: d'un service spécifique)"
    echo "  ps/status   - Voir l'état des services"
    echo "  rebuild     - Rebuild complet sans cache"
    echo "  clean       - Nettoyer les containers arrêtés"
    exit 1
    ;;
esac

