# Ordre d'installation et de setup recommandé

## 1. Setup environnement 
###  Dependencies de base
`code inline`
```bash
#Dependencies de base
pip install django djangorestframework psycopg2-binary timescaledb
pip freeze > requirements.txt
echo "../../v_energy_dbf" > .gitignore
```

## 2. Configuration base de données 
`code inline`
```bash
#Setup PostgreSQL + TimescaleDB localement (il est 13h26 14/02/2026, c'est ici que je suis)
#Configurer settings.py (DATABASES)
#Test connexion : 
python3 manage.py migrate
```
    







































