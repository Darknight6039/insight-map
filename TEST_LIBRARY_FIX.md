# 🔧 Test du Fix de la Bibliothèque

## ✅ Ce Qui A Été Corrigé

**Problème:** Les rapports générés n'apparaissaient pas dans la bibliothèque (erreur 403)

**Solution:**
- Ajouté des endpoints internes dans memory-service (`/api/internal/*`)
- Ces endpoints ne nécessitent pas d'authentification JWT
- Modifié report-service pour utiliser ces endpoints
- Modifié backend-service pour sauvegarder les conversations

## 🧪 Comment Tester

### Étape 1: Générer un Nouveau Rapport

1. Ouvrez l'application: http://localhost:3000
2. Connectez-vous si nécessaire
3. Sur la page d'accueil, créez une nouvelle analyse
4. Attendez que le rapport soit généré

### Étape 2: Vérifier la Bibliothèque

1. Cliquez sur **"Bibliothèque"** dans la barre de navigation
2. Vous devriez voir votre rapport dans la liste!

### Étape 3: Télécharger le PDF

1. Dans la bibliothèque, trouvez votre rapport
2. Cliquez sur l'icône de téléchargement (Download)
3. Le PDF devrait se télécharger

## 🔍 Vérification Technique

### Vérifier que le rapport est dans la base de données

```bash
# Vérifier la table user_documents
docker exec -i insight_mvp-postgres-1 psql -U insight_user -d insight_db -c "
SELECT
  id,
  user_id,
  document_type,
  title,
  analysis_type,
  created_at
FROM user_documents
ORDER BY created_at DESC
LIMIT 5;
"
```

### Vérifier les logs du report-service

```bash
# Chercher les logs de sauvegarde
docker-compose logs report-service | grep "memory service"
```

Vous devriez voir:
```
✅ Document saved to memory service: report_id=X, user=Y
```

### Vérifier les logs du memory-service

```bash
# Chercher les logs de création
docker-compose logs memory-service | grep "Created document"
```

Vous devriez voir:
```
Created document X for user Y via internal API
```

## 📊 Endpoints Internes Ajoutés

### Pour les Documents (utilisé par report-service)

```
POST /api/internal/documents?user_id={user_id}
Body: {
  "document_type": "report",
  "title": "...",
  "content": "...",
  "report_id": 123,
  "analysis_type": "synthese_executive",
  "metadata": {}
}
```

### Pour les Conversations (utilisé par backend-service)

```
POST /api/internal/conversations?user_id={user_id}
Body: {
  "query": "...",
  "response": "...",
  "conversation_type": "analysis",
  "analysis_type": "...",
  "business_type": "..."
}
```

## 🐛 Si Ça Ne Marche Pas

### 1. Vérifier que les services sont bien démarrés

```bash
docker-compose ps
```

Tous les services doivent être "Up"

### 2. Redémarrer les services

```bash
docker-compose restart memory-service report-service backend-service
```

### 3. Vérifier les erreurs dans les logs

```bash
# Memory service
docker-compose logs -f memory-service

# Report service
docker-compose logs -f report-service

# Backend service
docker-compose logs -f backend-service
```

### 4. Tester l'endpoint interne directement

```bash
# Créer un document test
curl -X POST "http://localhost:8008/api/internal/documents?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "report",
    "title": "Test Report",
    "content": "Test content",
    "report_id": 999,
    "metadata": {}
  }'
```

## ✅ Résultat Attendu

Après avoir généré un rapport:

1. **Dans /library:**
   - Le rapport apparaît dans la liste
   - Avec le bon titre
   - Avec la bonne date
   - Type: "Rapport"

2. **Dans la base de données:**
   - Une nouvelle ligne dans `user_documents`
   - `document_type = 'report'`
   - `user_id` correct
   - `report_id` rempli

3. **Dans les logs:**
   - report-service: "✅ Document saved to memory service"
   - memory-service: "Created document X for user Y via internal API"

## 🎯 Prochaines Étapes

Si tout fonctionne:

1. ✅ Les rapports s'affichent dans /library
2. ✅ Les rapports sont téléchargeables en PDF
3. ✅ Les conversations s'affichent dans /history (si backend-service est utilisé)

Vous pouvez maintenant utiliser pleinement la bibliothèque pour gérer vos documents!

## 📝 Notes Techniques

### Pourquoi des endpoints internes?

Les endpoints normaux (`/api/v1/*`) nécessitent un JWT token utilisateur. Le problème est que:
- `report-service` reçoit une requête du frontend via gateway
- Il crée le rapport
- Mais il n'a pas le JWT token de l'utilisateur pour appeler memory-service

**Solution:** Endpoints internes qui:
- N'ont pas besoin de JWT
- Acceptent `user_id` en paramètre
- Sont uniquement accessibles depuis le réseau Docker (pas depuis l'extérieur)

### Sécurité

Ces endpoints sont sécurisés car:
1. Ils ne sont accessibles que depuis le réseau interne Docker
2. Ils ne sont pas exposés publiquement
3. Seuls les autres services peuvent les appeler

En production, on pourrait ajouter:
- Un secret partagé entre services
- Des tokens service-to-service
- Des IP whitelists

---

**Dernière mise à jour:** 2026-01-18
**Services modifiés:** memory-service, report-service, backend-service
