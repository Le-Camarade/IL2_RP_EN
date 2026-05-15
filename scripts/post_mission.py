"""
Utilitaires post-génération de mission PWCG.

Commandes :
  python post_mission.py fix-lang
      Copie le .eng vers toutes les autres langues pour les missions PWCG
      dont les fichiers de langue diffèrent (ou sont vides).

  python post_mission.py journal YYYYMMDD "Texte de l'entrée"
      Ajoute une entrée dans le CampaignLog.json de la campagne active.
"""

import json
import shutil
import sys
from pathlib import Path

from config import get_il2_data_dir, get_pwcg_campaign_dir

LANG_EXTENSIONS = ["fra", "ger", "rus", "pol", "chs", "spa"]


def get_missions_dir() -> Path:
    return get_il2_data_dir() / "Missions" / "PWCG"


def get_active_campaign_dir() -> Path:
    """Retourne le dossier de la campagne la plus récemment modifiée."""
    campaigns_root = get_pwcg_campaign_dir() / "User" / "Campaigns"
    candidates = [
        d for d in campaigns_root.iterdir()
        if d.is_dir() and (d / "Campaign.json").exists()
    ]
    if not candidates:
        raise SystemExit("Aucune campagne trouvée dans PWCG_CAMPAIGN_DIR.")
    return max(candidates, key=lambda d: (d / "Campaign.json").stat().st_mtime)


def fix_languages():
    missions_dir = get_missions_dir()
    if not missions_dir.exists():
        raise SystemExit(f"Dossier missions introuvable : {missions_dir}")

    eng_files = list(missions_dir.glob("*.eng"))
    if not eng_files:
        print("Aucun fichier .eng trouvé.")
        return

    fixed = 0
    for eng in eng_files:
        stem = eng.stem  # ex: "Nicky Falstaff II 1944-11-01"
        for ext in LANG_EXTENSIONS:
            target = missions_dir / f"{stem}.{ext}"
            if not target.exists() or target.read_bytes() != eng.read_bytes():
                shutil.copy2(eng, target)
                fixed += 1
                print(f"  Copié : {target.name}")

    if fixed == 0:
        print("Tous les fichiers de langue sont déjà à jour.")
    else:
        print(f"{fixed} fichier(s) mis à jour.")


def add_journal_entry(date_yyyymmdd: str, text: str):
    campaign_dir = get_active_campaign_dir()
    log_file = campaign_dir / "CampaignLog.json"

    if not log_file.exists():
        raise SystemExit(f"CampaignLog.json introuvable : {log_file}")

    # Lire la campagne pour récupérer l'ID escadron joueur
    campaign_json = campaign_dir / "Campaign.json"
    campaign_name = json.loads(campaign_json.read_text(encoding="utf-8")).get("name", "")

    # Trouver l'ID escadron du joueur (serialNumber 1000001)
    squadron_id = _find_player_squadron(campaign_dir)

    data = json.loads(log_file.read_text(encoding="utf-8"))
    logs_by_date = data.setdefault("campaignLogsByDate", {})
    date_entry = logs_by_date.setdefault(date_yyyymmdd, {"date": date_yyyymmdd, "logs": []})
    date_entry["logs"].append({"log": text, "squadronId": squadron_id})

    log_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Journal [{date_yyyymmdd}] — entrée ajoutée ({campaign_name}, sqn {squadron_id}).")


def _find_player_squadron(campaign_dir: Path) -> int:
    for f in (campaign_dir / "Personnel").glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for pilot in data.get("squadronMemberCollection", {}).values():
                if pilot.get("serialNumber") == 1000001:
                    return pilot["squadronId"]
        except Exception:
            continue
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "fix-lang":
        fix_languages()
    elif cmd == "journal":
        if len(sys.argv) < 4:
            print("Usage : python post_mission.py journal YYYYMMDD \"Texte\"")
            sys.exit(1)
        add_journal_entry(sys.argv[2], sys.argv[3])
    else:
        print(f"Commande inconnue : {cmd}")
        print(__doc__)
        sys.exit(1)
