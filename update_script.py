import json
import datetime

# Ce script simule la mise à jour automatique
def update():
    try:
        with open('database.json', 'r') as f:
            data = json.load(f)
        
        data['last_updated'] = str(datetime.date.today())
        
        # Sauvegarde du fichier mis à jour
        with open('database.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("Mise à jour réussie.")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    update()
