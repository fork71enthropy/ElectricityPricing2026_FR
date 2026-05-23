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


# Choix Méthodologiques

## Pourquoi le Modèle d'Ornstein-Uhlenbeck ?

Les prix de l'électricité ont une propriété que la plupart des actifs financiers n'ont pas : la **mean-reversion**. Une action peut monter indéfiniment — Amazon est passé de 1$ à 3000$. L'électricité non — structurellement, les prix reviennent vers un équilibre dicté par les coûts de production.

Si le prix spike à 400 €/MWh, les centrales à gaz les plus chères s'allument, l'offre augmente, le prix redescend. Si le prix tombe à -100 €/MWh, les producteurs coupent leur production, l'offre baisse, le prix remonte. Il y a un mécanisme physique de retour à l'équilibre.

L'OU est le modèle stochastique le plus simple qui capture exactement ça — c'est pour ça que Schwartz (1997) l'a proposé pour les commodités et que c'est encore une référence aujourd'hui.

Le modèle de Black-Scholes — utilisé pour les actions — ne capture pas la mean-reversion. Il serait inapproprié ici.

---

## Pourquoi la Simulation Monte Carlo ?

Une fois le modèle OU calibré, il est impossible de calculer analytiquement "quel sera le prix dans 7 jours" — il y a trop d'incertitude. En revanche on peut simuler 10 000 trajectoires possibles et regarder la distribution des résultats. C'est ça Monte Carlo — remplacer le calcul exact par une simulation massive.

---

## Pourquoi un Industriel Veut Savoir le Prix la Semaine Prochaine ?

Imagine une aciérie qui consomme 50 MWh par heure, 24h/24. Sur une semaine :

```
50 MWh × 24h × 7j = 8 400 MWh
```

À 61 €/MWh en moyenne, la facture hebdomadaire est de **512 000 €**. Mais si le prix spike à 200 €/MWh pendant deux jours à cause d'une vague de froid, elle dépasse le million.

Cet industriel a deux options :

- Acheter son électricité au prix spot et subir la volatilité
- Acheter un contrat future ou une option pour fixer son prix à l'avance et sécuriser ses marges

Pour décider quelle couverture acheter — et à quel prix elle est justifiée — il a besoin de connaître la distribution probable des prix futurs. C'est exactement ce que le modèle fournit.

**La VaR à 95% lui dit quel budget maximum prévoir dans 95% des scénarios.** C'est de la gestion de risque appliquée à l'approvisionnement énergétique.

---

## Références

- Schwartz, E. (1997). *The Stochastic Behavior of Commodity Prices*. Journal of Finance.
- Lucia, J. & Schwartz, E. (2002). *Electricity Prices and Power Derivatives*. Review of Derivatives Research.