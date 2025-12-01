# Système Keep-Alive pour Media Auto Publish

## 🎯 Objectif

Maintenir le serveur Render actif et gérer automatiquement les publications en attente, même quand le serveur a été en sommeil.

## 📋 Ce qui a été ajouté

### 1. **Endpoint Backend** : `/posts/check-pending-posts`
- Vérifie tous les posts programmés dont la date est passée
- Les publie automatiquement
- Retourne un rapport détaillé

### 2. **Script Keep-Alive** : `keep_alive.py`
- Tourne sur votre machine locale
- Appelle le serveur toutes les 5 minutes
- Maintient le serveur éveillé
- Publie les posts en retard automatiquement

---

## 🚀 Installation et Configuration

### Étape 1 : Installer les dépendances

Sur votre machine locale :

```bash
pip install requests schedule
```

### Étape 2 : Configurer le script

Ouvrez `keep_alive.py` et modifiez la ligne :

```python
SERVER_URL = "https://votre-app.onrender.com"  # ← Remplacez par votre URL Render
```

**Exemple** : `https://media-auto-publish-abc123.onrender.com`

### Étape 3 : Lancer le script

```bash
python keep_alive.py
```

Vous verrez :

```
============================================================
  MEDIA AUTO PUBLISH - Keep Alive Service
============================================================
Serveur cible: https://votre-app.onrender.com
Intervalle: toutes les 5 minutes
Démarré le: 2025-12-01 15:30:00
============================================================

Appuyez sur Ctrl+C pour arrêter

[2025-12-01 15:30:00] ✓ Serveur actif
  → Posts en attente vérifiés: 2
  → Publiés: 2 | Échecs: 0
    ✓ Post #42 publié
    ✓ Post #43 publié
```

---

## 🔧 Personnalisation

Dans `keep_alive.py`, vous pouvez modifier :

```python
INTERVAL_MINUTES = 5  # Changez l'intervalle (min 5 min recommandé)
```

⚠️ **Attention** : Ne descendez pas en dessous de 5 minutes pour éviter de surcharger le serveur.

---

## 💡 Comment ça marche ?

1. **Toutes les 5 minutes**, le script envoie une requête à `/posts/check-pending-posts`
2. Le serveur **se réveille** s'il était endormi
3. L'endpoint **vérifie** tous les posts programmés
4. Si un post devait être publié à 15h mais le serveur dormait, **il sera publié au prochain réveil**
5. Le script affiche un **rapport** de chaque vérification

---

## 📊 Exemple de scénario

**Sans keep-alive** :
- 15h00 : Post programmé → ❌ Serveur dort, pas de publication
- 16h30 : Vous ouvrez l'app → Serveur se réveille, mais trop tard

**Avec keep-alive** :
- 15h00 : Post programmé → ❌ Serveur dort
- 15h05 : Script ping → ✅ Serveur se réveille, post publié immédiatement
- Maximum 5 minutes de retard

---

## 🖥️ Lancer le script en arrière-plan (Windows)

### Option 1 : Terminal toujours ouvert
Laissez simplement le terminal ouvert avec le script qui tourne.

### Option 2 : Tâche planifiée Windows
1. Créez un fichier `start_keepalive.bat` :
   ```bat
   @echo off
   cd /d "c:\PROG_HTML-JS-CSS\2025-11-28 - MEDIA AUTO PUBLISH"
   python keep_alive.py
   ```

2. Créez une tâche planifiée :
   - Ouvrez "Planificateur de tâches" Windows
   - Créer une tâche de base
   - Déclencheur : "Au démarrage de Windows"
   - Action : Démarrer un programme → `start_keepalive.bat`

---

## 🆓 Alternative : Service externe (sans script local)

Si vous ne voulez pas laisser votre machine allumée :

### **cron-job.org** (gratuit)

1. Allez sur [cron-job.org](https://cron-job.org)
2. Créez un compte
3. Ajoutez un nouveau cron job :
   - **URL** : `https://votre-app.onrender.com/posts/check-pending-posts`
   - **Méthode** : POST
   - **Intervalle** : Toutes les 5 minutes
   - **Titre** : Media Auto Publish Keep-Alive

✅ Le serveur sera maintenu actif automatiquement sans votre machine !

---

## 🔍 Test rapide

Pour tester manuellement l'endpoint :

```bash
curl -X POST https://votre-app.onrender.com/posts/check-pending-posts
```

Ou dans votre navigateur, installez une extension REST comme "Talend API Tester" et faites une requête POST.

---

## ⚠️ Important

- **Ne fermez pas** le terminal si vous utilisez le script local
- **Vérifiez régulièrement** que le script tourne toujours
- Le **maximum de retard** possible = INTERVAL_MINUTES (5 min par défaut)
- Le script **n'affecte pas** les publications futures normales (via APScheduler)

---

## 📞 Support

En cas de problème :
1. Vérifiez que `SERVER_URL` est correct
2. Testez manuellement l'endpoint avec curl
3. Vérifiez les logs du serveur Render
