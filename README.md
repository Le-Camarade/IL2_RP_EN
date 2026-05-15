# IL-2 Career Narrator

Couche narrative pour le mode carriere IL-2 Sturmovik, pilotee par **PWCG** (Pat Wilson's Campaign Generator) et **Claude Code**.

Chaque mission devient une experience : briefing par l'officier de renseignement, debriefing interactif, vie d'escadron au dispersal hut. Les donnees brutes du jeu et de PWCG alimentent une base Markdown persistante -- combat reports, fiches pilotes, journal d'escadron, memorial.

## Fonctionnalites

| Module | Description | Statut |
|--------|-------------|--------|
| **Brief** | Briefing immersif genere depuis les donnees PWCG avant la mission | En cours |
| **Debrief** | Debriefing interactif post-mission, croise avec les logs IL-2 | En cours |
| **Dispersal** | Roleplay avec les pilotes de l'escadron entre les missions | Planifie |

## Setup

### Prerequis

- **IL-2 Great Battles** avec `mission_text_log = 1` dans `startup.cfg`
- **PWCG** installe avec une campagne active
- **Python 3.10+**
- **Claude Code**

### Configuration

Copier `.env` et remplir les chemins :

```env
# Dossier data/ d'IL-2 (contient les missionReport*.txt)
IL2_DATA_DIR=C:\Program Files\IL-2 Sturmovik Great Battles\data

# Dossier de la campagne PWCG active
PWCG_CAMPAIGN_DIR=C:\...\PWCGBoS\User\Campaigns\MaCampagne
```

### Utilisation

Depuis le dossier du projet, ouvrir Claude Code :

```bash
claude
```

Puis :
- **Avant la mission** : *"Lance le briefing"*
- **Apres la mission** : *"Lance le debriefing"*
- **Entre les missions** : *"Dispersal"*

## Structure

```
IL2-Career-RP/
├── missions/           # Combat reports (un par sortie)
├── personnel/          # Fiches pilotes (joueur, allies, ennemis)
├── squadron/           # Journal, tableau de bord, memorial
├── scripts/            # Parsers Python (logs IL-2, JSON PWCG)
├── resources/          # Templates (formulaire RAF)
├── CLAUDE.md           # Instructions Claude Code
├── ROADMAP.md          # Etat d'avancement
└── .env                # Chemins IL-2 et PWCG
```

## Stack

- **Claude Code** : narration, debriefing interactif, roleplay
- **Python** : parsing des logs missionReport et des JSON PWCG
- **Markdown** : stockage de toute la narration (lisible dans Obsidian, VS Code, ou n'importe quoi)

## Ton

Sobre et militaire. Clostermann, pas Hollywood. Les pilotes ennemis sont traites avec le meme respect que les allies -- le memorial ne fait pas de distinction de camp.
