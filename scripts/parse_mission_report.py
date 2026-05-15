#!/usr/bin/env python3
"""Parse IL-2 missionReport*.txt files into a structured JSON summary."""

import re
import json
import sys
from pathlib import Path

from config import get_il2_data_dir


def parse_line(line: str) -> dict | None:
    line = line.strip()
    if not line:
        return None

    m = re.match(r"T:(\d+)\s+AType:(\d+)\s*(.*)", line)
    if not m:
        return None

    tick = int(m.group(1))
    atype = int(m.group(2))
    rest = m.group(3)

    fields = {}
    for km in re.finditer(r"(\w+):([^\s]+(?:\([^)]*\))?)", rest):
        key, val = km.group(1), km.group(2)
        pos_match = re.match(r"POS\(([^)]+)\)", val) if key == "POS" else None
        if key == "POS":
            pos_match = re.search(r"\(([^)]+)\)", val)
            if pos_match:
                coords = pos_match.group(1).split(",")
                fields["POS"] = {
                    "x": float(coords[0]),
                    "y": float(coords[1]),
                    "z": float(coords[2]),
                }
                continue
        fields[key] = val

    return {"tick": tick, "atype": atype, "fields": fields}


def build_summary(events: list[dict]) -> dict:
    objects = {}
    spawns = []
    hits = []
    damages = []
    kills = []
    takeoffs = []
    landings = []
    mission_info = {}

    for ev in events:
        at = ev["atype"]
        f = ev["fields"]

        if at == 0:
            mission_info = {
                "gdate": f.get("GDate", ""),
                "gtime": f.get("GTime", ""),
                "mfile": f.get("MFile", ""),
            }

        elif at == 12:
            obj_id = f.get("ID", "")
            obj = {
                "id": obj_id,
                "type": f.get("TYPE", ""),
                "country": int(f.get("COUNTRY", "0")),
                "name": f.get("NAME", ""),
                "pid": int(f.get("PID", "-1")),
                "pos": f.get("POS"),
            }
            objects[obj_id] = obj
            spawns.append({"tick": ev["tick"], **obj})

        elif at == 1:
            hits.append({
                "tick": ev["tick"],
                "attacker_id": f.get("AID", ""),
                "target_id": f.get("TID", ""),
            })

        elif at == 2:
            damages.append({
                "tick": ev["tick"],
                "attacker_id": f.get("AID", ""),
                "target_id": f.get("TID", ""),
                "damage": f.get("DMG", ""),
            })

        elif at == 3:
            kills.append({
                "tick": ev["tick"],
                "attacker_id": f.get("AID", ""),
                "target_id": f.get("TID", ""),
            })

        elif at == 5:
            takeoffs.append({"tick": ev["tick"], "id": f.get("ID", "")})

        elif at == 6:
            landings.append({"tick": ev["tick"], "id": f.get("ID", "")})

    def resolve(obj_id: str) -> dict:
        obj = objects.get(obj_id, {})
        return {
            "id": obj_id,
            "type": obj.get("type", "unknown"),
            "country": obj.get("country", 0),
            "name": obj.get("name", ""),
        }

    player_id = None
    player_obj = None
    for obj in objects.values():
        if obj["pid"] != -1:
            player_id = obj["id"]
            player_obj = obj
            break

    allied = [o for o in objects.values() if o["country"] == 102]
    axis = [o for o in objects.values() if o["country"] == 201]

    resolved_kills = []
    for k in kills:
        resolved_kills.append({
            "tick": k["tick"],
            "attacker": resolve(k["attacker_id"]),
            "victim": resolve(k["target_id"]),
        })

    player_kills = [k for k in resolved_kills if k["attacker"].get("id") == player_id]
    player_deaths = [k for k in resolved_kills if k["victim"].get("id") == player_id]

    return {
        "mission": mission_info,
        "player": player_obj,
        "allied_aircraft": [{"type": o["type"], "name": o["name"]} for o in allied],
        "axis_aircraft": [{"type": o["type"], "name": o["name"]} for o in axis],
        "kills": resolved_kills,
        "player_kills": player_kills,
        "player_deaths": player_deaths,
        "total_hits": len(hits),
        "total_damages": len(damages),
        "takeoffs": len(takeoffs),
        "landings": len(landings),
    }


def load_reports(log_dir: Path) -> list[dict]:
    events = []
    files = sorted(log_dir.glob("missionReport*.txt"))
    if not files:
        print(f"Aucun missionReport*.txt trouvé dans {log_dir}", file=sys.stderr)
        sys.exit(1)

    for f in files:
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            parsed = parse_line(line)
            if parsed:
                events.append(parsed)

    events.sort(key=lambda e: e["tick"])
    return events


def main():
    log_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else get_il2_data_dir()
    events = load_reports(log_dir)
    summary = build_summary(events)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
