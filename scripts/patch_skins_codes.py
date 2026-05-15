"""
Applique le skin Le Flandres à tous les pilotes du 326 Sqn
et renumérote les avions en 1, 2, 3... (triés par serialNumber).
"""

import json
from pathlib import Path

CAMPAIGN = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common"
    r"\IL-2 Sturmovik Battle of Stalingrad\PWCGBoS\User\Campaigns\Nicky Falstaff II"
)
PERSONNEL_FILE = CAMPAIGN / "Personnel" / "103084326.json"
EQUIPMENT_FILE = CAMPAIGN / "Equipment" / "103084326.json"

SKIN_ENTRY = {
    "skinName": "SpitfireMkIXe_Le_Flandre",
    "planeType": "spitfiremkixe",
    "archTypes": [],
    "startDate": "19410601",
    "endDate": "19450503",
    "squadId": -1,
    "country": "Britain",
    "category": "",
    "definedInGame": False,
    "winter": False,
    "useTacticalCodes": False,
    "tacticalCodeType": "PATTERN_UNDEFINED",
    "tacticalCodeColor": "NONE",
}


def patch_personnel():
    data = json.loads(PERSONNEL_FILE.read_text(encoding="utf-8"))
    changed = 0
    for pilot in data["squadronMemberCollection"].values():
        already = any(s["skinName"] == SKIN_ENTRY["skinName"] for s in pilot["skins"])
        if not already:
            pilot["skins"].append(SKIN_ENTRY)
            changed += 1
    PERSONNEL_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Personnel : skin ajouté à {changed} pilote(s).")


def patch_equipment():
    data = json.loads(EQUIPMENT_FILE.read_text(encoding="utf-8"))
    planes = data["equippedPlanes"]
    # Trier par serialNumber croissant
    sorted_serials = sorted(planes.keys(), key=lambda k: planes[k]["serialNumber"])
    import string
    letters = list(string.ascii_uppercase)
    for i, key in enumerate(sorted_serials):
        planes[key]["aircraftIdCode"] = letters[i]
    EQUIPMENT_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Equipment : {len(sorted_serials)} avion(s) renommés A-{letters[len(sorted_serials)-1]}.")


if __name__ == "__main__":
    patch_personnel()
    patch_equipment()
    print("Terminé.")
