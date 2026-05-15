#!/usr/bin/env python3
"""Read PWCG campaign JSON files and extract relevant data for the narrator."""

import json
import sys
from pathlib import Path

from config import get_pwcg_campaign_dir


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_campaign(campaign_dir: Path) -> dict:
    campaign_file = campaign_dir / "Campaign.json"
    if not campaign_file.exists():
        print(f"Campaign.json introuvable dans {campaign_dir}", file=sys.stderr)
        sys.exit(1)

    campaign = load_json(campaign_file)
    return {
        "name": campaign.get("name", ""),
        "date": campaign.get("date", ""),
        "product": campaign.get("product", ""),
        "campaign_mode": campaign.get("campaignMode", ""),
        "map": campaign.get("initialMap", ""),
    }


def read_personnel(campaign_dir: Path) -> list[dict]:
    personnel_dir = campaign_dir / "Personnel"
    if not personnel_dir.exists():
        return []

    pilots = []
    for f in personnel_dir.glob("*.json"):
        data = load_json(f)
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict) and "pilots" in data:
            entries = data["pilots"]
        elif isinstance(data, dict):
            entries = [data]
        else:
            continue

        for p in entries:
            if not isinstance(p, dict):
                continue
            pilots.append({
                "name": p.get("name", p.get("pilotName", "")),
                "rank": p.get("rank", ""),
                "skill": p.get("skill", p.get("aiSkillLevel", "")),
                "victories": p.get("victories", p.get("airVictories", 0)),
                "status": p.get("status", p.get("pilotActiveStatus", "Active")),
                "squadron": f.stem,
                "serial": p.get("serialNumber", ""),
            })

    return pilots


def read_combat_reports(campaign_dir: Path, pilot_serial: str = None) -> list[dict]:
    cr_dir = campaign_dir / "CombatReports"
    if not cr_dir.exists():
        return []

    reports = []
    search_dirs = [cr_dir / pilot_serial] if pilot_serial else cr_dir.iterdir()

    for d in search_dirs:
        if not isinstance(d, Path):
            d = Path(d)
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.json")):
            report = load_json(f)
            reports.append({
                "file": f.name,
                "date": report.get("date", ""),
                "squadron": report.get("squadron", ""),
                "pilot": report.get("reportPilotName", ""),
                "duty": report.get("duty", ""),
                "narrative": report.get("narrative", ""),
                "ha_report": report.get("haReport", ""),
                "flight_pilots": report.get("flightPilots", []),
            })

    return reports


def read_equipment(campaign_dir: Path) -> list[dict]:
    eq_dir = campaign_dir / "Equipment"
    if not eq_dir.exists():
        return []

    equipment = []
    for f in eq_dir.glob("*.json"):
        data = load_json(f)
        equipment.append({"squadron": f.stem, "data": data})

    return equipment


def main():
    campaign_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else get_pwcg_campaign_dir()
    pilot_serial = sys.argv[2] if len(sys.argv) > 2 else None

    result = {
        "campaign": read_campaign(campaign_dir),
        "personnel": read_personnel(campaign_dir),
        "combat_reports": read_combat_reports(campaign_dir, pilot_serial),
        "equipment": read_equipment(campaign_dir),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
