# Applications Django

## Architecture
- **core** : Modèles de base (TimeStampedModel, utilitaires)
- **data_collection** : Récupération API entsoe + cache
- **analytics** : Calculs CO2, agrégations temporelles
- **dashboard** : API REST pour le frontend

## Flux de données
1. data_collection récupère depuis RTE
2. analytics traite et calcule
3. dashboard expose via API REST
4. frontend consomme l'API

### Première exploration dans 01_exploratory.ipynb
```python
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

df = pd.read_sql("SELECT * FROM data_collection_spotprice ORDER BY start_date", engine)
print(df.shape)
df.head()
df.describe()
```
1. count : nombre ou bien cardinal
2. mean : moyenne ou espérance
3. std : écart type, mesure de la dispertion autour de la moyenne
4. min : prix minimum enregistré
5. 25% : 25% des prix en dessous de 
6. 50%
7. 75%
8. max