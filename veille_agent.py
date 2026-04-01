import os
import json
import datetime
import urllib.request
import ssl
import xml.etree.ElementTree as ET
import urllib.request
import json
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

RSS_FEEDS = [
    "https://www.reddit.com/r/editors/search.rss?q=AAF&sort=new&t=week",
    "https://www.reddit.com/r/premiere/search.rss?q=AAF+export&sort=new&t=week",
    "https://www.reddit.com/r/Avid/search.rss?q=AAF&sort=new&t=week",
    "https://www.reddit.com/r/VideoEditing/search.rss?q=AAF+error&sort=new&t=week",
    "https://www.reddit.com/r/davinciresolve/search.rss?q=AAF&sort=new&t=week",
]

def fetch_rss_posts():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    posts = []
    for url in RSS_FEEDS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AAFDropnCheck-Veille/1.0"})
            with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
                content = r.read().decode("utf-8")
            root = ET.fromstring(content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                link = entry.find("atom:link", ns)
                if title is not None:
                    posts.append({
                        "title": title.text or "",
                        "text": (summary.text or "")[:500] if summary is not None else "",
                        "url": link.get("href", "") if link is not None else ""
                    })
        except Exception as e:
            print(f"Erreur RSS {url}: {e}")
    print(f"{len(posts)} posts collectes.")
    return posts

def analyze_with_ai(posts):
    if not posts:
        return []
    compiled = "\n\n".join([
        f"TITRE: {p['title']}\nCONTENU: {p['text']}" for p in posts[:30]
    ])
    prompt = """Tu es un expert en post-production audio et video.
Analyse ces posts de forums. Ignore les plaintes non techniques.
Isole uniquement les bugs averes lies aux exports/imports AAF, OMF, ou aux echanges NLE vers DAW.
Reponds UNIQUEMENT avec un tableau JSON strict, sans texte avant ou apres.
Chaque objet doit avoir exactement ces champs :
- code : le code erreur ou mot-cle technique
- software : le logiciel source
- issue : description courte en francais
- recommendation : action corrective en francais
- reliability_score : score de 0 a 100
Si aucun bug AAF n'est trouve, reponds avec : []

""" + compiled

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            response = json.loads(r.read().decode("utf-8"))
        raw = response["candidates"][0]["content"]["parts"][0]["text"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        errors = json.loads(raw)
        print(f"{len(errors)} erreurs detectees.")
        return errors
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        return []

def update_quarantine(new_errors):
    pending_file = "pending_errors.json"
    if os.path.exists(pending_file):
        with open(pending_file, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = {"pending": [], "last_updated": ""}
    existing["pending"].extend(new_errors)
    existing["last_updated"] = str(datetime.date.today())
    existing["count"] = len(existing["pending"])
    with open(pending_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)
    print(f"Quarantaine mise a jour : {len(existing['pending'])} erreurs en attente.")

if __name__ == "__main__":
    posts = fetch_rss_posts()
    errors = analyze_with_ai(posts)
    if errors:
        update_quarantine(errors)
    else:
        print("Aucune nouvelle erreur detectee cette semaine.")
