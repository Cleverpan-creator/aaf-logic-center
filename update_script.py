import json
import datetime

def update():
    # Notre bibliothèque d'erreurs AAF (Table de référence)
    aaf_errors = [
        {
            "code": "FFFFFC2B",
            "software": "Adobe Premiere Pro",
            "issue": "Sample Rate Mismatch / Corrupt Media",
            "recommendation": "Convertir tous les fichiers audio en WAV 48kHz / 24-bit avant l'export.",
            "reliability_score": 90
        },
        {
            "code": "Essence Data Write Error",
            "software": "Adobe Premiere Pro",
            "issue": "Echec d'encapsulage (Embedded)",
            "recommendation": "Utiliser l'option 'Separate Audio' au lieu de 'Embedded' ou repasser en version 25.0.",
            "reliability_score": 85
        },
        {
            "code": "CM_OFFSET_OUT_OF_RANGE",
            "software": "Avid Media Composer",
            "issue": "Media Database Corruption",
            "recommendation": "Supprimer les fichiers .pmr et .mdb dans le dossier Avid MediaFiles et laisser reconstruire.",
            "reliability_score": 95
        },
        {
            "code": "Failed to encode audio clip",
            "software": "DaVinci Resolve",
            "issue": "Permission ou Speed Change",
            "recommendation": "Faire un 'Render in Place' sur les clips avec effets de vitesse avant l'export AAF.",
            "reliability_score": 80
        }
    ]

    try:
        # Création de la structure finale
        data = {
            "last_updated": str(datetime.date.today()),
            "status": "Production",
            "errors": aaf_errors
        }
        
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print("Base de données mise à jour avec les codes d'erreurs.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")

if __name__ == "__main__":
    update()
