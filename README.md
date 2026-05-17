# IL-2 Career Narrator

Narrative layer for IL-2 Sturmovik career mode, driven by **PWCG** (Pat Wilson's Campaign Generator) and **Claude Code**.

Each mission becomes an experience: briefing by the intelligence officer, interactive debriefing, squadron life at the dispersal hut. Raw data from the game and PWCG feeds a persistent Markdown base — combat reports, pilot sheets, squadron journal, memorial.

## Features

| Module | Description | Status |
|--------|-------------|--------|
| **Brief** | Immersive briefing generated from PWCG data before the mission | In progress |
| **Debrief** | Interactive post-mission debriefing, cross-referenced with IL-2 logs | In progress |
| **Dispersal** | Roleplay with squadron pilots between missions | Planned |

## Setup

### Prerequisites

- **IL-2 Great Battles** with `mission_text_log = 1` in `startup.cfg`
- **PWCG** installed with an active campaign
- **Python 3.10+**
- **Claude Code**

### Configuration

Copy `.env` and fill in the paths:

```env
# IL-2 data/ folder (contains missionReport*.txt)
IL2_DATA_DIR=C:\Program Files\IL-2 Sturmovik Great Battles\data

# Active PWCG campaign folder
PWCG_CAMPAIGN_DIR=C:\...\PWCGBoS\User\Campaigns\MaCampagne
```

### Usage

From the project folder, open Claude Code:

```bash
claude
```

Then:
- **Before the mission**: *"Launch the briefing"*
- **After the mission**: *"Launch the debriefing"*
- **Between missions**: *"Dispersal"*

## Structure

```
IL2-Career-RP/
├── missions/           # Combat reports (one per sortie)
├── personnel/          # Pilot sheets (player, allies, enemies)
├── squadron/           # Journal, dashboard, memorial
├── scripts/            # Python parsers (IL-2 logs, PWCG JSON)
├── resources/          # Templates (RAF form)
├── CLAUDE.md           # Claude Code instructions
├── ROADMAP.md          # Progress status
└── .env                # IL-2 and PWCG paths
```

## Stack

- **Claude Code**: narration, interactive debriefing, roleplay
- **Python**: parsing of missionReport logs and PWCG JSON files
- **Markdown**: storage for all narration (readable in Obsidian, VS Code, or anything)

## Tone

Sober and military. Clostermann, not Hollywood. Enemy pilots are treated with the same respect as allies — the memorial makes no distinction between sides.
