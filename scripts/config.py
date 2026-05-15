"""Charge les chemins depuis .env à la racine du projet."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env() -> dict[str, str]:
    env = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip().strip('"').strip("'")
        if val:
            env[key.strip()] = val
    return env


def get_il2_data_dir() -> Path:
    env = load_env()
    raw = env.get("IL2_DATA_DIR")
    if not raw:
        raise SystemExit("IL2_DATA_DIR non défini dans .env")
    return Path(raw)


def get_pwcg_campaign_dir() -> Path:
    env = load_env()
    raw = env.get("PWCG_CAMPAIGN_DIR")
    if not raw:
        raise SystemExit("PWCG_CAMPAIGN_DIR non défini dans .env")
    return Path(raw)
