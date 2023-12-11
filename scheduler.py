# scheduler.py
import schedule
import time
from utils_api import update_prices  # Importez la fonction du script

# Planifie l'exécution toutes les 6 heures
schedule.every(4).hours.do(update_prices)

# Boucle pour exécuter le planificateur en continu
while True:
    schedule.run_pending()
    time.sleep(1)
