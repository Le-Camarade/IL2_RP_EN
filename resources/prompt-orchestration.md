# Orchestration — Flux de commandes

## Commandes reconnues

Le joueur tape un mot-clé dans Claude Code. Claude détecte l'intention et déclenche le workflow correspondant.

| Déclencheur | Workflow | Prompt IO |
|-------------|----------|-----------|
| `briefing`, `brief`, `avant la mission` | Briefing pré-mission | `prompt-io-briefing.md` |
| `debrief`, `debriefing`, `je suis rentré`, `après la mission` | Debriefing post-mission | `prompt-io-debrief.md` |
| `dispersal`, `entre les missions`, `au bar` | Dispersal hut (Phase 3) | À définir |

Tout autre message est traité normalement (question sur le projet, demande technique, etc.).

---

## Workflow Briefing — pas à pas

```
JOUEUR: "briefing"
    │
    ▼
CLAUDE (silencieux):
    1. python scripts/post_mission.py fix-lang  (génère .fra/.ger/etc.)
    2. Lire Campaign.json → extraire date (YYYYMMDD)
    3. Lire MissionData/Nicky Falstaff II YYYY-MM-DD.MissionData.json
       → Si absent : briefing contextuel + note "générer dans PWCG"
    3. Lire squadron/tableau-de-bord.md
    4. Lire les 3 dernières entrées de squadron/journal.md
    5. Convertir toutes les unités SI → impérial (feet, mph)
    │
    ▼
CLAUDE (hors personnage):
    Sauvegarder missions/briefings/YYYY-MM-DD_briefing-NN.md
    │
    ▼
CLAUDE (en personnage IO):
    Affiche le briefing structuré (voir prompt-io-briefing.md)
    Règle : pas de noms ni effectifs ennemis — unités + types uniquement
    │
    ▼
JOUEUR: questions éventuelles
    │
    ▼
CLAUDE (IO): répond en personnage
    │
    ▼
JOUEUR: "je vais voler" / "c'est bon" / "go"
    │
    ▼
CLAUDE (IO): "Compris. On se retrouve au debrief."
    Fin du workflow briefing.
```

---

## Workflow Debriefing — pas à pas

```
JOUEUR: "debrief"
    │
    ▼
CLAUDE (silencieux):
    1. python scripts/parse_mission_report.py
       → Si aucun missionReport trouvé : "Pas de logs de mission.
         Tu as bien activé mission_text_log dans startup.cfg ?"
       → Identifier les logs les plus récents (par timestamp dans le nom)
    2. python scripts/parse_pwcg.py
    3. Lire squadron/tableau-de-bord.md
    4. Stocker le résumé en mémoire de travail (pas affiché)
    │
    ▼
CLAUDE (en personnage IO):
    Commence la Phase 1 de l'interrogatoire.
    UNE question à la fois.
    │
    ▼
    ┌─────────────────────────────┐
    │  Boucle interrogatoire      │
    │  Phase 1 → 2 → 3 → 4 → 5  │
    │  → 6                        │
    │  Adapter selon les réponses │
    │  Sauter si déjà couvert     │
    └─────────────────────────────┘
    │
    ▼
CLAUDE (IO):
    Annonce les résultats confirmés.
    "Je rédige le rapport."
    │
    ▼
CLAUDE (hors personnage):
    Génère les fichiers :
    1. missions/YYYY-MM-DD_mission-NN.md  (combat report)
    2. Mise à jour personnel/             (fiches pilotes)
    3. Mise à jour squadron/journal.md    (entrée courte)
    4. Mise à jour squadron/tableau-de-bord.md
    5. Mise à jour squadron/memorial.md   (si tombés)
    │
    ▼
CLAUDE: "Rapport classé. Tu veux passer au dispersal ?"
```

---

## Sélection des logs récents

Les `missionReport*.txt` s'accumulent dans `IL2_DATA_DIR`. Pour trouver les bons :

1. Lister tous les `missionReport(*)*.txt`
2. Extraire le timestamp du nom : `missionReport(YYYY-MM-DD_HH-MM-SS)[N].txt`
3. Grouper par timestamp (tous les `[N]` d'une même session)
4. Prendre le groupe le **plus récent**
5. Si plusieurs groupes du même jour : demander au joueur lequel

---

## Numérotation des missions

Le numéro `NN` dans `missions/YYYY-MM-DD_mission-NN.md` est séquentiel :
- Compter les fichiers existants dans `missions/` (hors dossier `briefings/`)
- Incrémenter de 1
- Format : deux chiffres, zéro-padded (`01`, `02`, ... `99`)

Le briefing associé utilise le **même numéro** : `missions/briefings/YYYY-MM-DD_briefing-NN.md`

---

## Workflow Dispersal — pas à pas

```
JOUEUR: "dispersal"
    │
    ▼
CLAUDE (silencieux):
    1. Lire squadron/tableau-de-bord.md
    2. Lire les 3-5 dernières entrées de squadron/journal.md
    3. Lire personnel/allies/*.md (fiches pilotes vivants)
    4. Lire le dernier missions/*.md
    5. Choisir 2-4 pilotes présents (cohérent avec contexte)
    │
    ▼
CLAUDE (en personnage — narrateur + pilotes):
    Plante le décor en 2-3 phrases.
    Un pilote lance un échange (ou silence).
    │
    ▼
    ┌──────────────────────────────────────┐
    │  Boucle libre                        │
    │  Le joueur parle → pilotes réagissent│
    │  Pilotes parlent entre eux           │
    │  Joueur intervient ou observe        │
    │  Pas de durée imposée               │
    └──────────────────────────────────────┘
    │
    ▼
JOUEUR: "je vais me coucher" / "j'y vais" / coupe la session
    │
    ▼
CLAUDE (hors personnage):
    1. Entrée dans squadron/journal.md (ambiance, 3-5 lignes)
    2. Mise à jour personnel/allies/*.md si évolution notable
    "Session dispersal enregistrée."
```

**Première session dispersal d'une campagne** : si les fichiers `personnel/allies/*.md` n'existent pas encore, Claude les génère d'abord à partir des données PWCG (parse_pwcg.py), puis lance le dispersal normalement.

---

## Transition entre workflows

Le joueur peut enchaîner :
```
briefing → vole la mission → debrief → dispersal
```

Ou revenir plus tard :
```
debrief    (seul, après avoir volé)
dispersal  (seul, quand il veut)
```

Chaque workflow est autonome — il lit l'état courant des fichiers, pas un état en mémoire de la session précédente. Ça permet de reprendre après un redémarrage de Claude Code.

---

## Gestion d'erreurs

| Problème | Réaction |
|----------|----------|
| `.env` vide ou chemins invalides | "Les chemins dans .env ne sont pas configurés. Vérifie IL2_DATA_DIR et PWCG_CAMPAIGN_DIR." |
| Pas de missionReport récent | "Pas de logs de mission trouvés. Tu as bien mission_text_log = 1 dans startup.cfg ?" |
| PWCG Campaign.json absent | "Je ne trouve pas de campagne PWCG au chemin configuré. Vérifie PWCG_CAMPAIGN_DIR dans .env." |
| MissionData absent | Briefing contextuel (historique + escadron) + "Génère la mission dans PWCG pour les objectifs précis." |
| Personnel vide | "Pas de données pilotes. La campagne PWCG est bien initialisée ?" |
| Logs d'une ancienne mission | "Les derniers logs datent de [date]. C'est bien cette mission ?" |
