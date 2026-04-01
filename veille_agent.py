import os
import json
import datetime
import praw
import anthropic

# --- CONFIGURATION VIA SECRETS ---
REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

SUBREDDITS = ["editors", "premiere", "Avid", "VideoEditing", "davinciresolve"]
KEYWORDS = ["AAF", "OMF", "Pro Tools", "export audio", "AAF error", "AAF import"]
DAYS_BACK = 7

def collect_reddit_posts():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent="AAFDropnCheck-Veille/1.0"
    )
    posts = []
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=DAYS_BACK)
    for sub in SUBREDDITS:
        try:
            for submission in reddit.subreddit(sub).new(limit=100):
                if datetime.datetime.utcfromtimestamp(submission.created_utc) < cutoff:
                    continue
                text = f"{submission.title} {submission.selftext}"
                if any(kw.lower() in text.lower() for kw in KEYWORDS):
                    posts.append({
                        "source": f"r/{sub}",
                        "title": submission.title,
                        "text": submission.selftext[:500],
                        "url": submission.url
                    })
        except Exception as e:
            print(f"Erreur r/{sub}: {e}")
    print(f"{len(posts)} posts collectes.")
    return posts

def analyze_with_ai(posts):
    if not posts:
        return []
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    compiled = "\n\n".join([
        f"[{p['source']}] {p['title']}\n{p['text']}" for p in posts
    ])
    system_prompt = """Tu es un expert en post-production audio et video.
Analyse ces posts de forums. Ignore les plaintes non techniques et les questions generales.
Isole uniquement les bugs averes lies aux exports/imports AAF, OMF, ou aux echanges NLE vers DAW.
Reponds UNIQUEMENT avec un tableau JSON strict, sans texte avant ou apres.
Chaque objet doit avoir exactement ces champs :
- code : le code erreur ou mot-cle technique (ex: FFFFFC2B, Essence Data Write Error)
- software : le logiciel source du probleme (ex: Premiere Pro, Avid Media Composer, DaVinci Resolve)
- issue : description courte du probleme en francais
- recommendation : action corrective concrete en francais
- reliability_score : score de 0 a 100 base sur la frequence et la precision des rapports
Si aucun bug technique AAF n'est trouve, reponds avec un tableau vide : []"""

    message = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": compiled}]
    )
    raw = message.content[0].text.strip()
    try:
        errors = json.loads(raw)
        print(f"{len(errors)} erreurs detectees par l'IA.")
        return errors
    except json.JSONDecodeError:
        print(f"Erreur de parsing JSON : {raw[:200]}")
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
    posts = collect_reddit_posts()
    errors = analyze_with_ai(posts)
    if errors:
        update_quarantine(errors)
    else:
        print("Aucune nouvelle erreur detectee cette semaine.")
