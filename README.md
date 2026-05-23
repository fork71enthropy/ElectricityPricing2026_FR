# ElectricityPricing_FR

> Plateforme fullstack de modélisation quantitative des prix spot de l'électricité française  
> Candidat Master Mathématiques Appliquées — Recherche stage Finance de l'Énergie / Modélisation Quantitative

---

## Vision du Projet

Ce projet est un moteur de modélisation quantitative des marchés électriques français, construit de bout en bout sans framework de haut niveau ni génération de code automatique. Il combine ingénierie logicielle réelle — pipeline de données, base de données, API REST — et mathématiques financières appliquées : calibration d'un processus stochastique de mean-reversion, simulation Monte Carlo, calcul de VaR.

Ce n'est pas un dashboard de visualisation. C'est un système complet qui tourne sur des données de marché réelles.

---

## Fondements Mathématiques

### Modèle d'Ornstein-Uhlenbeck (Mean-Reversion)

L'électricité présente une forte mean-reversion — contrairement aux actions, les prix reviennent vers un niveau d'équilibre structurel. On modélise le prix spot par :

```
dS(t) = κ(μ - S(t))dt + σ dW(t)
```

- **κ** — vitesse de retour à la moyenne
- **μ** — niveau d'équilibre long terme
- **σ** — volatilité instantanée
- **W(t)** — mouvement brownien standard

Estimation des paramètres par **maximum de vraisemblance (MLE)** sur l'historique des prix spot ENTSO-E.

### Simulation Monte Carlo

Une fois les paramètres calibrés, on génère N trajectoires de prix simulées pour :

- Estimer la distribution des prix futurs
- Calculer une **Value at Risk (VaR) à 95%** sur un horizon donné
- Visualiser les intervalles de confiance sur les scénarios de prix

```
S(t+dt) = S(t) + κ(μ - S(t))dt + σ√dt · ε,   ε ~ N(0,1)
```

---

## Ce qui a été construit

### Pipeline de données réel

- Connexion à l'**API ENTSO-E Transparency Platform** (authentification par token, requêtes REST)
- Récupération de **35 494 enregistrements** de prix day-ahead français (janvier 2024 — avril 2026), granularité 15 minutes
- Stockage en **PostgreSQL** via Django ORM
- Collecte automatique quotidienne via **cron job** + management command Django

### Infrastructure backend

- **Django 5** + **Django REST Framework**
- **PostgreSQL** comme base de données principale
- Modèle `SpotPrice` avec contrainte `unique_together` sur les timestamps pour éviter les doublons
- Variables d'environnement via `.env` (credentials jamais committés)
- Architecture modulaire : `apps/data_collection/` avec `collect.py`, `models.py`, `management/commands/collect_prices.py`

### Analyse exploratoire (en cours)

- Chargement des 35k enregistrements dans un DataFrame pandas via SQLAlchemy
- Statistiques descriptives : mean=61.43 €/MWh, std=45.27, min=-478 €/MWh, max=473 €/MWh
- Notebook `01_exploratory.ipynb` en cours de développement

---

## Stack Technique

| Composant | Technologie | Rôle |
|---|---|---|
| Backend | Django 5 · DRF | API REST, collecte données |
| Base de données | PostgreSQL | Stockage séries temporelles |
| Source de données | API ENTSO-E Transparency Platform | Prix spot day-ahead français |
| Modélisation | NumPy · SciPy · Statsmodels | Calibration MLE, simulation MC |
| Exploration | Pandas · Jupyter · Matplotlib | Analyse statistique |
| Frontend (à venir) | React · Plotly.js | Visualisation interactive |

---

## Architecture

```
ElectricityPricing_FR/
├── apps/
│   └── data_collection/
│       ├── collect.py              # Client ENTSO-E + sauvegarde BDD
│       ├── models.py               # Modèle SpotPrice
│       └── management/
│           └── commands/
│               └── collect_prices.py  # Management command Django
├── Energy_Dashboard_France/
│   └── settings.py                 # Config Django + PostgreSQL
├── notebooks/
│   └── 01_exploratory.ipynb       # Analyse statistique (en cours)
├── .env.example                    # Template credentials
├── requirements.txt
└── manage.py
```

---

## Roadmap — 8 Semaines

### ✅ Semaine 1 — Collecte et Stockage des Données
- [x] Connexion API ENTSO-E et récupération de 35 494 prix spot historiques
- [x] Modèle Django + PostgreSQL pour stocker les séries temporelles
- [x] Script de collecte automatique quotidienne (cron job)

### 🔄 Semaine 2 — Analyse Exploratoire (en cours)
- [x] Notebook `01_exploratory.ipynb` : statistiques descriptives des prix spot
- [x] Visualisation saisonnalité, autocorrélation, détection des pics
- [x] Vérification de la stationnarité (test ADF)

### Semaine 3 — Calibration du Modèle OU
- [ ] Implémentation de la log-vraisemblance du processus OU
- [ ] Estimation des paramètres κ, μ, σ par `scipy.optimize`
- [ ] Notebook `02_calibration.ipynb` : résultats et validation du modèle

### Semaine 4 — Simulation Monte Carlo
- [ ] Moteur de simulation vectorisé (numpy) — N=10 000 trajectoires
- [ ] Calcul de la VaR à 95% sur horizon 7 jours
- [ ] Tests unitaires sur la simulation

### Semaine 5 — API REST Backend
- [ ] Endpoints DRF : prix historiques, paramètres calibrés, scénarios MC
- [ ] Serializers et documentation des endpoints
- [ ] Tests d'intégration API

### Semaine 6 — Frontend React
- [ ] Composant `PriceChart` : prix spot historiques (Plotly.js)
- [ ] Composant `ModelParams` : affichage κ, μ, σ avec interprétation
- [ ] Connexion frontend ↔ API backend

### Semaine 7 — Visualisation Monte Carlo
- [ ] Composant `MonteCarloChart` : N trajectoires simulées + intervalles de confiance
- [ ] Affichage VaR 95% sur le graphique
- [ ] Contrôle interactif de l'horizon de simulation

### Semaine 8 — Finalisation
- [ ] Tests end-to-end
- [ ] Déploiement (AWS EC2 ou Railway)
- [ ] Documentation finale

---

## Résultat Final Attendu

Une plateforme fullstack accessible via navigateur permettant de :

1. **Visualiser** l'historique des prix spot français (2024-2026) avec granularité 15 min
2. **Consulter** les paramètres κ, μ, σ calibrés sur les données réelles
3. **Simuler** N=10 000 trajectoires de prix futurs via Monte Carlo
4. **Lire** la VaR à 95% sur un horizon configurable

Le tout alimenté par un pipeline de données automatisé qui collecte chaque jour les nouveaux prix publiés sur ENTSO-E.

---

## Observations sur les Données

Les 35 494 enregistrements révèlent déjà des patterns caractéristiques du marché électrique français :

- **Prix négatifs récurrents** (min = -478 €/MWh) lors des pics de production solaire/éolienne en période de faible demande — les producteurs paient littéralement les acheteurs pour écouler leur production
- **Forte saisonnalité journalière** — les prix nocturnes sont structurellement inférieurs aux prix de pointe (17h-21h)
- **Mean-reversion visible** — après chaque pic extrême, les prix reviennent vers l'équilibre autour de 61 €/MWh

---

## Références

- Schwartz, E. (1997). *The Stochastic Behavior of Commodity Prices*. Journal of Finance.
- Lucia, J. & Schwartz, E. (2002). *Electricity Prices and Power Derivatives*. Review of Derivatives Research.

---

## Auteur

Candidat Master Mathématiques Appliquées  
Recherche stage Finance de l'Énergie / Modélisation Quantitative  
[github.com/fork71enthropy](https://github.com/fork71enthropy)