# ROADMAP — IL-2 Career Narrator (PWCG)

## Phase 1 — Parsers et fondations

### 1.1 Parser missionReport (logs AType)
- [x] Script `parse_mission_report.py` : lit tous les `missionReport*.txt` d'une session
- [x] Reconstruit la timeline : spawns (AType:12), hits (1), dégâts (2), kills (3), décollages (5), atterrissages (6)
- [x] Résout les ID : associe chaque ID à un TYPE + COUNTRY + NAME
- [x] Identifie le pilote joueur (PID != -1) et son appareil
- [x] Produit un JSON structuré sur stdout
- [ ] **À valider sur de vrais logs** — en attente première mission PWCG

### 1.2 Lecteur PWCG
- [x] Script `parse_pwcg.py` : lit les JSON PWCG pertinents
- [x] Extrait : liste des pilotes escadron (nom, rang, skill, victoires, statut)
- [x] Extrait : combat reports PWCG (pour croisement)
- [x] Extrait : équipement par escadron
- [ ] **À valider sur de vrais JSON PWCG** — en attente première campagne

### 1.3 Configuration et structure
- [x] `.env` avec chemins `IL2_DATA_DIR` et `PWCG_CAMPAIGN_DIR`
- [x] `config.py` — chargement .env partagé par tous les scripts
- [x] Template `combat-report-template.md` (formulaire RAF Form 540/F)
- [x] `squadron/tableau-de-bord.md` — structure prête
- [x] `squadron/journal.md` — prêt
- [x] `squadron/memorial.md` — prêt
- [ ] Initialisation automatique des fiches pilotes depuis PWCG

---

## Phase 2 — Brief / Debrief

### 2.1 Briefing
- [x] Prompt système IO briefing (`resources/prompt-io-briefing.md`)
- [x] Structure : situation, mission, composition vol, opposition, météo, consignes
- [x] Flux d'orchestration documenté (`resources/prompt-orchestration.md`)
- [ ] **À valider sur une vraie mission PWCG**

### 2.2 Debriefing interactif
- [x] Prompt système IO debrief (`resources/prompt-io-debrief.md`)
- [x] Séquence de questions structurée (6 phases)
- [x] Logique de croisement récit joueur vs données logs
- [x] Gestion cas limites (logs absents, mission sans contact, crash)
- [ ] Génération du Combat Report (`missions/YYYY-MM-DD_mission-NN.md`) — **à tester**
- [ ] Mise à jour des fiches pilotes — **à tester**
- [ ] Mise à jour tableau de bord + journal — **à tester**

---

## Phase 3 — Dispersal

### 3.1 Profils pilotes
- [x] Système de profils défini : traits (tempérament, combat, société), relation, backstory, état courant
- [x] Logique de génération depuis données PWCG (rang → ancien/nouveau, skill → as/vert, nom → nationalité)
- [x] Stockés dans `personnel/allies/[nom].md`
- [ ] **À tester** : génération initiale sur vrais pilotes PWCG

### 3.2 Interactions
- [x] Prompt dispersal complet (`resources/prompt-dispersal.md`)
- [x] Pilotes se parlent entre eux, joueur s'insère quand il veut
- [x] Sujets naturels définis (mission en biais, permissions, bouffe, mort banalisée)
- [x] Anti-patterns listés (pas de monologues héroïques, pas de narration 2e personne)
- [x] Logging dans `squadron/journal.md`
- [ ] **À tester** sur une vraie session

### 3.3 Évolution
- [x] Relations qui changent selon les événements
- [x] Moral escadron qui influe sur le ton
- [x] Mémoire persistante via fiches pilotes
- [ ] Rotation des pilotes (arrivées, départs) — à affiner avec les données PWCG

---

## Phase 4 — Enrichissements (plus tard)

- [ ] Mémorial enrichi avec biographies fictives des tombés
- [ ] Fiches ennemis abattus (biographie cohérente, unité, parcours)
- [ ] Newspaper clippings fictifs (communiqués, citations)
- [ ] Interface web locale (Flask, localhost)

---

## Prochaine étape

1. Nicolas crée une campagne PWCG dédiée
2. Remplir `.env` avec les vrais chemins
3. Valider les parsers sur de vraies données
4. Premier brief + debrief complet sur une mission réelle
