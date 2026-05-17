# Orchestration — Command Flow

## Recognised Commands

The player types a keyword in Claude Code. Claude detects the intent and triggers the corresponding workflow.

| Trigger | Workflow | IO Prompt |
|---------|----------|-----------|
| `briefing`, `brief`, `avant la mission` | Pre-mission briefing | `prompt-io-briefing.md` |
| `debrief`, `debriefing`, `je suis rentré`, `après la mission` | Post-mission debriefing | `prompt-io-debrief.md` |
| `dispersal`, `entre les missions`, `au bar` | Dispersal hut (Phase 3) | To be defined |

Any other message is handled normally (question about the project, technical request, etc.).

---

## Briefing Workflow — Step by Step

```
PLAYER: "briefing"
    │
    ▼
CLAUDE (silent):
    1. python scripts/post_mission.py fix-lang  (generates .fra/.ger/etc.)
    2. Read Campaign.json → extract date (YYYYMMDD)
    3. Read MissionData/Nicky Falstaff II YYYY-MM-DD.MissionData.json
       → If absent: contextual briefing + note "generate in PWCG"
    3. Read squadron/tableau-de-bord.md
    4. Read last 3 entries of squadron/journal.md
    5. Convert all SI units → imperial (feet, mph)
    │
    ▼
CLAUDE (out of character):
    Save missions/briefings/YYYY-MM-DD_briefing-NN.md
    │
    ▼
CLAUDE (in character as IO):
    Display structured briefing (see prompt-io-briefing.md)
    Rule: no enemy names or strength figures — units + types only
    │
    ▼
PLAYER: any questions
    │
    ▼
CLAUDE (IO): responds in character
    │
    ▼
PLAYER: "je vais voler" / "c'est bon" / "go"
    │
    ▼
CLAUDE (IO): "Understood. See you at the debrief."
    End of briefing workflow.
```

---

## Debriefing Workflow — Step by Step

```
PLAYER: "debrief"
    │
    ▼
CLAUDE (silent):
    1. Read raw logs manually:
       → List missionReport(*)*.txt, identify the most recent session by timestamp
       → Read [0].txt: aircraft IDs (AType:12/10), enemy groups (AType:11)
       → Search all files: AType:3 kills, AType:2 allied damage,
         AType:6 landings, AID:-1 flak
       → Intermediate AType:12: identify enemy aircraft types/names
       → If no missionReport found: "No mission logs found.
         Have you enabled mission_text_log in startup.cfg?"
    2. python scripts/parse_mission_report.py (supplement — may miss kills on AType:11)
    3. python scripts/parse_pwcg.py
    4. Read squadron/tableau-de-bord.md
    5. Store summary in working memory (not displayed)
    │
    ▼
CLAUDE (in character as IO):
    Begins Phase 1 of the debrief.
    ONE question at a time.
    │
    ▼
    ┌─────────────────────────────┐
    │  Debrief loop               │
    │  Phase 1 → 2 → 3 → 4 → 5  │
    │  → 6                        │
    │  Adapt to answers given     │
    │  Skip if already covered    │
    └─────────────────────────────┘
    │
    ▼
CLAUDE (IO):
    Announces confirmed results.
    "I'll write up the report."
    │
    ▼
CLAUDE (out of character):
    Generates files:
    1. missions/combat_reports/YYYY-MM-DD_mission-NN.md  (combat report)
    2. Update personnel/             (pilot files)
    3. Update squadron/journal.md    (short entry)
    4. Update squadron/tableau-de-bord.md
    5. Update squadron/memorial.md   (if casualties)
    6. python scripts/post_mission.py journal YYYYMMDD "text"
       → inject into PWCG CampaignLog.json
    │
    ▼
CLAUDE: "Report filed. Shall we head to the dispersal?"
```

---

## Selecting Recent Logs

`missionReport*.txt` files accumulate in `IL2_DATA_DIR`. To find the right ones:

1. List all `missionReport(*)*.txt`
2. Extract the timestamp from the filename: `missionReport(YYYY-MM-DD_HH-MM-SS)[N].txt`
3. Group by timestamp (all `[N]` files from the same session)
4. Take the **most recent** group
5. If multiple groups from the same day: ask the player which one

---

## Mission Numbering

The `NN` in `missions/combat_reports/YYYY-MM-DD_mission-NN.md` is sequential:
- Count existing files in `missions/combat_reports/`
- Increment by 1
- Format: two digits, zero-padded (`01`, `02`, ... `99`)

The associated briefing uses the **same number**: `missions/briefings/YYYY-MM-DD_briefing-NN.md`

---

## Dispersal Workflow — Step by Step

```
PLAYER: "dispersal"
    │
    ▼
CLAUDE (silent):
    1. Read squadron/tableau-de-bord.md
    2. Read last 3–5 entries of squadron/journal.md
    3. Read personnel/allies/*.md (living pilot files)
    4. Read the latest missions/combat_reports/*.md
    5. Select 2–4 pilots present (consistent with context)
    │
    ▼
CLAUDE (in character — narrator + pilots):
    Sets the scene in 2–3 sentences.
    A pilot opens a conversation (or silence).
    │
    ▼
    ┌──────────────────────────────────────┐
    │  Free-running loop                   │
    │  Player speaks → pilots react        │
    │  Pilots talk among themselves        │
    │  Player steps in or observes         │
    │  No imposed duration                 │
    └──────────────────────────────────────┘
    │
    ▼
PLAYER: "je vais me coucher" / "j'y vais" / ends the session
    │
    ▼
CLAUDE (out of character):
    1. Entry in squadron/journal.md (atmosphere, 3–5 lines)
    2. Update personnel/allies/*.md if notable change
    "Dispersal session logged."
```

**First dispersal session of a campaign**: if `personnel/allies/*.md` files do not yet exist, Claude generates them first from the PWCG data (parse_pwcg.py), then launches the dispersal normally.

---

## Transitions Between Workflows

The player may chain them:
```
briefing → fly the mission → debrief → dispersal
```

Or return later:
```
debrief    (on its own, after flying)
dispersal  (on its own, whenever)
```

Each workflow is self-contained — it reads the current state of the files, not an in-memory state from the previous session. This allows resuming after a Claude Code restart.

---

## Error Handling

| Problem | Response |
|---------|----------|
| `.env` empty or invalid paths | "The paths in .env are not configured. Check IL2_DATA_DIR and PWCG_CAMPAIGN_DIR." |
| No recent missionReport | "No mission logs found. Do you have mission_text_log = 1 in startup.cfg?" |
| PWCG Campaign.json missing | "Cannot find a PWCG campaign at the configured path. Check PWCG_CAMPAIGN_DIR in .env." |
| MissionData missing | Contextual briefing (historical + squadron context) + "Generate the mission in PWCG for precise objectives." |
| Personnel empty | "No pilot data found. Has the PWCG campaign been properly initialised?" |
| Logs from an old mission | "The latest logs are dated [date]. Is that the mission you want?" |
