# 🔍 Guide : Vérifier les Tokens Restants sur votre Clé API Perplexity

## Méthode 1 : Via le Dashboard Web (Recommandé)

### Étapes

1. **Connectez-vous à votre compte Perplexity**
   - Allez sur [https://www.perplexity.ai](https://www.perplexity.ai)
   - Connectez-vous avec vos identifiants

2. **Accédez aux paramètres API**
   - Cliquez sur votre profil (en haut à droite)
   - Sélectionnez **"Settings"** ou **"Paramètres"**
   - Allez dans l'onglet **"API"**

3. **Consultez votre quota**
   - Vous verrez votre **utilisation actuelle**
   - Votre **solde de crédits restants**
   - Les **limites de votre plan**
   - L'**historique d'utilisation**

4. **Ajouter des crédits (si nécessaire)**
   - Si votre solde est insuffisant, vous pouvez ajouter des crédits directement depuis cette page

**URL directe** : [https://www.perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)

---

## Méthode 2 : Via l'Endpoint de Vérification (Dans votre Application)

### Endpoint Ajouté

J'ai ajouté un endpoint `/check-api-status` qui teste votre clé API et détecte les erreurs de quota.

### Utilisation

```bash
# Vérifier le statut de votre clé API
curl http://localhost:8006/check-api-status | jq
```

### Réponses Possibles

#### ✅ Clé Valide et Fonctionnelle
```json
{
  "status": "success",
  "api_key_configured": true,
  "api_key_valid": true,
  "test_model": "sonar",
  "message": "✅ Clé API valide et fonctionnelle",
  "note": "Pour vérifier votre quota exact, consultez https://www.perplexity.ai/settings/api"
}
```

#### ⚠️ Quota Dépassé
```json
{
  "status": "error",
  "api_key_configured": true,
  "api_key_valid": true,
  "error_type": "quota_exceeded",
  "message": "⚠️ Quota dépassé ou limite de taux atteinte",
  "suggestion": "Consultez votre quota sur https://www.perplexity.ai/settings/api et ajoutez des crédits si nécessaire"
}
```

#### ❌ Clé Invalide
```json
{
  "status": "error",
  "api_key_configured": true,
  "api_key_valid": false,
  "error_type": "unauthorized",
  "message": "❌ Clé API invalide ou expirée",
  "suggestion": "Vérifiez votre clé sur https://www.perplexity.ai/settings/api"
}
```

---

## Méthode 3 : Via les Logs de l'Application

### Surveiller les Erreurs de Quota

Les erreurs de quota apparaissent dans les logs avec le code d'erreur `429` :

```bash
# Voir les erreurs récentes
docker compose logs --since 1h backend-service | grep "API error"

# Filtrer spécifiquement les erreurs de quota
docker compose logs --since 1h backend-service | grep -E "429|quota|rate limit"
```

### Exemples d'Erreurs

```
ERROR: Perplexity API error with sonar-pro: 429 Rate limit exceeded
ERROR: Perplexity API error with sonar: Quota exceeded
```

---

## Méthode 4 : Test Manuel avec curl

### Test Direct de l'API

```bash
# Remplacer YOUR_API_KEY par votre vraie clé
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 10
  }'
```

### Interprétation des Réponses

- **200 OK** : Clé valide, quota disponible
- **401 Unauthorized** : Clé invalide ou expirée
- **429 Too Many Requests** : Quota dépassé ou limite de taux atteinte
- **402 Payment Required** : Crédits insuffisants

---

## Surveillance Continue

### Script de Monitoring (Optionnel)

Vous pouvez créer un script pour vérifier régulièrement :

```bash
#!/bin/bash
# check-quota.sh

RESPONSE=$(curl -s http://localhost:8006/check-api-status)
STATUS=$(echo $RESPONSE | jq -r '.status')

if [ "$STATUS" = "error" ]; then
    ERROR_TYPE=$(echo $RESPONSE | jq -r '.error_type')
    if [ "$ERROR_TYPE" = "quota_exceeded" ]; then
        echo "⚠️ ALERTE: Quota Perplexity dépassé!"
        # Envoyer une notification (email, Slack, etc.)
    fi
fi
```

### Intégration dans votre Monitoring

Ajoutez `/check-api-status` à votre système de monitoring (Prometheus, Datadog, etc.) pour être alerté automatiquement en cas de problème.

---

## FAQ

### Q: Perplexity fournit-il un endpoint API pour vérifier le quota exact ?

**R:** Non, Perplexity ne fournit pas d'endpoint API public pour vérifier le quota exact. Il faut passer par leur dashboard web.

### Q: Comment savoir combien de tokens j'ai utilisés ce mois-ci ?

**R:** Consultez votre dashboard sur [https://www.perplexity.ai/settings/api](https://www.perplexity.ai/settings/api). Vous y trouverez l'historique d'utilisation détaillé.

### Q: Que faire si mon quota est dépassé ?

**R:** 
1. Allez sur [https://www.perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
2. Ajoutez des crédits à votre compte
3. Ou attendez le renouvellement mensuel de votre plan

### Q: Les erreurs 429 signifient-elles toujours un quota dépassé ?

**R:** Pas toujours. L'erreur 429 peut aussi signifier :
- **Rate limiting** : Trop de requêtes en peu de temps
- **Quota dépassé** : Crédits insuffisants
- **Limite de plan** : Limite mensuelle atteinte

Dans tous les cas, vérifiez votre dashboard pour plus de détails.

---

## Résumé des Méthodes

| Méthode | Précision | Facilité | Temps Réel |
|---------|-----------|----------|------------|
| Dashboard Web | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ |
| Endpoint `/check-api-status` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |
| Logs Application | ⭐⭐ | ⭐⭐⭐ | ✅ |
| Test curl manuel | ⭐⭐⭐ | ⭐⭐ | ✅ |

**Recommandation** : Utilisez le **Dashboard Web** pour une vue précise de votre quota, et l'**endpoint `/check-api-status`** pour une vérification rapide depuis votre application.

---

**Dernière mise à jour** : Décembre 2024  
**Documentation Perplexity** : [https://docs.perplexity.ai/](https://docs.perplexity.ai/)

