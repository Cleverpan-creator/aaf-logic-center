import json
import datetime
import os

def update():
    aaf_errors = [
        {
            "code": "FFFFFC2B",
            "software": "Adobe Premiere Pro",
            "issue": "Sample Rate Mismatch",
            "recommendation": "Convertir en WAV 48kHz / 24-bit.",
            "reliability_score": 90
        },
        {
            "code": "Essence Data Write Error",
            "software": "Adobe Premiere Pro",
            "issue": "Echec d'encapsulage",
            "recommendation": "Utiliser 'Separate Audio' ou Premiere 25.0.",
            "reliability_score": 85
        }
    ]

    try:
        data = {
            "last_updated": str(datetime.date.today()),
            "status": "Production",
            "errors": aaf_errors
        }
        
        # On vérifie si le fichier existe, sinon on le crée proprement
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Succès : database.json mis à jour.")
            
    except Exception as e:
        print(f"Erreur : {e}")
        exit(1) # Informe GitHub que ça a échoué

if __name__ == "__main__":
    update()
