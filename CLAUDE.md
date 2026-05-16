# CLAUDE.md — IL-2 Career Narrator (PWCG)

## Contexte

Module de roleplay narratif pour le mode carrière IL-2 Sturmovik, piloté par **PWCG** (Pat Wilson's Campaign Generator). Claude Code transforme les données brutes PWCG + logs IL-2 en narration persistante : briefings, debriefings, vie d'escadron.

Interface principale : **terminal** via Claude Code.

---

## Pilote joueur

À déterminer automatiquement via les fichiers PWCG au lancement de la campagne. Le script `parse_pwcg.py` identifie le pilote joueur, son appareil, son unité et sa campagne.

---

## Configuration — .env

Le fichier `.env` à la racine contient les chemins vers les données IL-2 et PWCG. Les scripts lisent ces chemins automatiquement.

```env
# Dossier IL-2 contenant les missionReport*.txt
IL2_DATA_DIR=C:\Program Files\IL-2 Sturmovik Great Battles\data

# Dossier campagne PWCG active
PWCG_CAMPAIGN_DIR=C:\...\PWCGBoS\User\Campaigns\MaCampagne
```

Prérequis IL-2 : `mission_text_log = 1` dans `startup.cfg` (section `[KEY = system]`).

---

## Sources de données

### 1. Fichiers PWCG (JSON)

Chemin typique : `<IL-2 install>/PWCGBoS/User/Campaigns/<CampaignName>/`

| Fichier | Contenu | Usage |
|---------|---------|-------|
| `Campaign.json` | Date campagne, carte, mode | Contexte temporel et géographique |
| `Personnel/<SquadronID>.json` | Pilotes : nom, rang, skill, victoires, statut | Fiches pilotes, dispersal |
| `CombatReports/<PilotSerial>/YYYYMMDD.CombatReport.json` | Rapport post-mission PWCG | Croisement avec debrief |
| `MissionData/Nicky Falstaff II YYYY-MM-DD.MissionData.json` | Paramètres de la mission générée (duty, météo, appareils, escorte) | Briefing |
| `Equipment/` | Appareils disponibles par escadron | Contexte matériel |

### 2. Fichier .Mission (texte structuré)

Généré par PWCG dans `data/Multiplayer/Cooperative/`. Contient la structure complète : waypoints, objectifs, avions, météo. Format texte avec blocs imbriqués (`Plane {}`, `MCU_Waypoint {}`, `Options {}`).

### 3. Logs missionReport (texte, AType)

Générés par IL-2 dans `<IL-2 install>/data/` si `mission_text_log = 1` dans `startup.cfg`. Une mission produit **plusieurs fichiers** numérotés :

```
missionReport(2026-05-15_20-30-45)[0].txt
missionReport(2026-05-15_20-30-45)[1].txt
...
```

Chaque ligne suit le format : `T:<timestamp> AType:<N> <clés:valeurs>`

ATypes critiques :

| AType | Événement | Champs clés |
|-------|-----------|-------------|
| 0 | MissionStart | GDate, GTime, MFile |
| 1 | Hit | AID (attaquant), TID (cible) |
| 2 | Damage | AID, TID, pourcentage dégâts |
| 3 | Kill | AID (attaquant), TID (victime) |
| 5 | TakeOff | ID |
| 6 | Landing | ID |
| 12 | ObjectSpawned | ID, TYPE, COUNTRY, NAME, POS |

**COUNTRY:102** = Alliés | **COUNTRY:201** = Axe

---

## Architecture du projet

```
IL2-Career-RP/
├── CLAUDE.md                        ← ce fichier
├── ROADMAP.md                       ← phases du projet
│
├── missions/
│   ├── YYYY-MM-DD_mission-NN.md     ← un combat report par sortie
│   └── briefings/
│       └── YYYY-MM-DD_briefing-NN.md ← un briefing par sortie
│
├── personnel/
│   ├── [pilote-joueur].md           ← fiche pilote joueur (généré depuis PWCG)
│   ├── allies/                      ← équipiers de l'escadron
│   │   └── [prenom-nom].md
│   └── axis/                        ← pilotes ennemis rencontrés/abattus
│       └── [prenom-nom].md
│
├── squadron/
│   ├── journal.md                   ← dispersal hut — vie entre les missions
│   ├── tableau-de-bord.md           ← stats escadron, effectif, moral
│   └── memorial.md                  ← tous les tombés, alliés et ennemis
│
├── logs/                            ← réservé aux exports manuels si besoin
│
├── resources/
│   └── combat-report-template.md    ← template formulaire RAF
│
└── scripts/
    ├── parse_mission_report.py      ← parser logs AType → JSON structuré
    └── parse_pwcg.py                ← lecteur fichiers PWCG JSON
```

---

## Workflows — Prompts IO et orchestration

Trois workflows déclenchés par mot-clé. Chaque workflow est documenté en détail dans `resources/`.

| Mot-clé | Workflow | Prompt détaillé |
|---------|----------|-----------------|
| `briefing` | Briefing pré-mission | `resources/prompt-io-briefing.md` |
| `debrief` | Debriefing post-mission interactif | `resources/prompt-io-debrief.md` |
| `dispersal` | Roleplay dispersal hut | `resources/prompt-dispersal.md` |

Logique de séquencement, gestion d'erreurs, sélection des logs : `resources/prompt-orchestration.md`.

### Briefing — résumé

1. Lancer `python scripts/post_mission.py fix-lang` (silencieux) — génère les fichiers de langue `.fra`, `.ger`, etc. pour la mission PWCG
2. Lire `Campaign.json` pour obtenir la date campagne (`YYYYMMDD`)
3. Lire `MissionData/Nicky Falstaff II YYYY-MM-DD.MissionData.json` (date campagne courante)
   - Si absent : briefing contextuel uniquement + note au joueur de générer la mission dans PWCG
3. Lire `squadron/tableau-de-bord.md` + dernières entrées `squadron/journal.md`
4. Sauvegarder le briefing dans `missions/briefings/YYYY-MM-DD_briefing-NN.md`
5. Afficher le briefing **en personnage IO** (structure dans `prompt-io-briefing.md`)
6. Répondre aux questions du joueur en personnage
7. Quand le pilote part voler : "Compris. On se retrouve au debrief."

**Règles IO briefing :**
- Toutes les unités en **feet et mph** (jamais mètres ou m/s) — convertir les données PWCG
- Ne jamais citer les noms des pilotes ennemis ni leur effectif précis avant le combat
- L'opposition attendue = unités et types d'appareils probables (contexte historique), pas les données MissionData ennemies

### Debriefing — résumé

1. Lancer `python scripts/parse_mission_report.py` sur les logs les plus récents (silencieux)
2. Lancer `python scripts/parse_pwcg.py` (silencieux)
3. Stocker les données — **ne pas les montrer au joueur**
4. Interrogatoire **en personnage IO**, une question à la fois (6 phases dans `prompt-io-debrief.md`)
5. Croiser le récit du joueur avec les logs. Brouillard de guerre normal.
6. Annoncer les résultats confirmés
7. Générer les fichiers :
   - `missions/YYYY-MM-DD_mission-NN.md` — Combat Report RAF
   - Mise à jour `personnel/` (pilote, alliés touchés, ennemis abattus)
   - `squadron/journal.md` — entrée courte
   - `squadron/tableau-de-bord.md` — stats mises à jour
   - `squadron/memorial.md` — si tombés
8. Lancer `python scripts/post_mission.py journal YYYYMMDD "texte"` — injecte l'entrée de `squadron/journal.md` dans le `CampaignLog.json` PWCG

### Dispersal — résumé

1. Lire `squadron/tableau-de-bord.md`, `squadron/journal.md`, `personnel/allies/*.md`, dernier `missions/*.md`
2. Choisir 2-4 pilotes présents (cohérent avec le contexte)
3. Planter le décor en 2-3 phrases
4. Faire vivre les pilotes — chacun réagit selon son profil, pas selon un script
5. Le joueur parle quand il veut, les pilotes se parlent aussi entre eux
6. À la fin : entrée dans `squadron/journal.md` + mise à jour fiches pilotes si évolution

---

## Ton narratif

- **Combat Reports** : formulaire inspiré RAF Form 540/F, rédigé en français. Sobre, factuel, daté.
- **Journal dispersal** : Pierre Clostermann (*Le Grand Cirque*). Humain, précis, pince-sans-rire.
- **Fiches pilotes ennemis** : biographies fictives cohérentes avec la période et l'unité.
- **Pilotes alliés** : personnalités émergentes basées sur leur historique.
- **Langue** : tout en français. Seuls les termes techniques et noms d'unité restent en anglais (squadron, flight, flak, angels, etc.).

---

## Contraintes

- Tout est stocké **en local**, aucun cloud
- Les fichiers Markdown sont lisibles sans outil spécial
- Ne pas inventer de données absentes des logs — signaler les lacunes
- Le ton reste sobre et militaire, jamais héroïque
- Les pilotes ennemis sont traités avec respect — le mémorial ne fait pas de distinction de camp
