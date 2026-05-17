# ROADMAP — IL-2 Career Narrator (PWCG)

## Phase 1 — Parsers and foundations

### 1.1 missionReport parser (AType logs)
- [x] Script `parse_mission_report.py`: reads all `missionReport*.txt` from a session
- [x] Reconstructs the timeline: spawns (AType:12), hits (1), damage (2), kills (3), takeoffs (5), landings (6)
- [x] Resolves IDs: associates each ID with a TYPE + COUNTRY + NAME
- [x] Identifies the player pilot (PID != -1) and their aircraft
- [x] Produces structured JSON on stdout
- [ ] **To validate on real logs** — awaiting first PWCG mission

### 1.2 PWCG reader
- [x] Script `parse_pwcg.py`: reads the relevant PWCG JSON files
- [x] Extracts: squadron pilot list (name, rank, skill, victories, status)
- [x] Extracts: PWCG combat reports (for cross-reference)
- [x] Extracts: equipment per squadron
- [ ] **To validate on real PWCG JSON** — awaiting first campaign

### 1.3 Configuration and structure
- [x] `.env` with paths `IL2_DATA_DIR` and `PWCG_CAMPAIGN_DIR`
- [x] `config.py` — shared .env loading for all scripts
- [x] Template `combat-report-template.md` (RAF Form 540/F)
- [x] `squadron/tableau-de-bord.md` — structure ready
- [x] `squadron/journal.md` — ready
- [x] `squadron/memorial.md` — ready
- [ ] Automatic pilot sheet initialisation from PWCG

---

## Phase 2 — Brief / Debrief

### 2.1 Briefing
- [x] IO briefing system prompt (`resources/prompt-io-briefing.md`)
- [x] Structure: situation, mission, flight composition, opposition, weather, instructions
- [x] Orchestration flow documented (`resources/prompt-orchestration.md`)
- [ ] **To validate on a real PWCG mission**

### 2.2 Interactive debriefing
- [x] IO debrief system prompt (`resources/prompt-io-debrief.md`)
- [x] Structured question sequence (6 phases)
- [x] Cross-reference logic: player account vs log data
- [x] Edge case handling (missing logs, mission without contact, crash)
- [ ] Combat Report generation (`missions/YYYY-MM-DD_mission-NN.md`) — **to test**
- [ ] Pilot sheet updates — **to test**
- [ ] Dashboard + journal updates — **to test**

---

## Phase 3 — Dispersal

### 3.1 Pilot profiles
- [x] Profile system defined: traits (temperament, combat, social), relationship, backstory, current state
- [x] Generation logic from PWCG data (rank → veteran/new, skill → ace/green, name → nationality)
- [x] Stored in `personnel/allies/[nom].md`
- [ ] **To test**: initial generation on real PWCG pilots

### 3.2 Interactions
- [x] Full dispersal prompt (`resources/prompt-dispersal.md`)
- [x] Pilots talk among themselves, player joins whenever they want
- [x] Natural topics defined (mission debated sideways, leave, food, death normalised)
- [x] Anti-patterns listed (no heroic monologues, no second-person narration)
- [x] Logging in `squadron/journal.md`
- [ ] **To test** on a real session

### 3.3 Evolution
- [x] Relationships changing according to events
- [x] Squadron morale influencing tone
- [x] Persistent memory via pilot sheets
- [ ] Pilot rotation (arrivals, departures) — to refine with PWCG data

---

## Phase 4 — Enhancements (later)

- [ ] Memorial enriched with fictional biographies of the fallen
- [ ] Enemy pilot sheets for kills (coherent biography, unit, career)
- [ ] Fictional newspaper clippings (communiqués, citations)
- [ ] Local web interface (Flask, localhost)

---

## Next steps

1. Nicolas creates a dedicated PWCG campaign
2. Fill in `.env` with real paths
3. Validate parsers on real data
4. First full brief + debrief on a real mission
