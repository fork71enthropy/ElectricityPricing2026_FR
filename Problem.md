# Problème

## Contexte

Le marché spot de l'électricité française est l'un des plus volatils au monde. Les prix day-ahead — négociés chaque jour sur EPEX Spot pour livraison le lendemain — peuvent osciller entre **-478 €/MWh** (surproduction solaire extrême un jour de faible demande) et **+473 €/MWh** (tension extrême sur le réseau en période de froid). Sur les données historiques 2024-2026, l'écart-type atteint **45 €/MWh** pour une moyenne de **61 €/MWh** — soit une volatilité relative de 74%.

Cette volatilité est structurelle : l'électricité ne se stocke pas. À chaque instant, production et consommation doivent s'équilibrer. Un excès de production solaire un samedi ensoleillé fait chuter les prix en territoire négatif. Une vague de froid inattendue les fait exploser. Le marché réagit en temps réel, sans amortisseur.

## Le Problème

**Les acteurs exposés au prix spot — industriels, fournisseurs d'énergie, traders — ne disposent pas d'un outil simple et rigoureux pour quantifier leur risque de prix sur un horizon court terme.**

Sans modèle, un industriel qui consomme 10 MWh par heure ne sait pas répondre à cette question : *dans le pire des cas raisonnables, combien vais-je payer mon électricité la semaine prochaine ?*

Répondre à cette question nécessite trois choses :

1. **Un modèle stochastique** calibré sur des données réelles, qui capture les propriétés statistiques des prix spot — notamment la mean-reversion : les prix dévient fortement mais reviennent systématiquement vers un niveau d'équilibre
2. **Un moteur de simulation** capable de générer des milliers de trajectoires de prix futurs plausibles
3. **Une mesure de risque** — la Value at Risk (VaR) à 95% — qui synthétise la distribution simulée en un chiffre actionnable

## La Solution

Ce projet implémente un pipeline complet :

**Données réelles** — 35 494 prix day-ahead français (janvier 2024 — avril 2026, granularité 15 min) collectés via l'API ENTSO-E Transparency Platform et stockés en PostgreSQL.

**Modèle d'Ornstein-Uhlenbeck** — le modèle stochastique de référence pour les commodités à mean-reversion, calibré par maximum de vraisemblance (MLE) sur l'historique réel :

```
dS(t) = κ(μ - S(t))dt + σ dW(t)
```

**Simulation Monte Carlo** — N = 10 000 trajectoires de prix simulées sur un horizon de 7 jours :

```
S(t+dt) = S(t) + κ(μ - S(t))dt + σ√dt · ε,   ε ~ N(0,1)
```

**VaR à 95%** — le seuil de prix que 95% des trajectoires simulées ne dépassent pas sur l'horizon considéré. Un résultat concret, directement utilisable pour la gestion du risque.

## Ce que ce projet n'est pas

Ce n'est pas un dashboard de visualisation de données publiques. C'est un moteur de modélisation quantitative qui transforme un historique de prix en une distribution probabiliste des prix futurs, avec une mesure de risque associée — le type d'outil qu'un desk énergie ou un fonds spécialisé commodités utilise pour piloter son exposition.