import json
from pathlib import Path


PREFERENCES_PATH = Path("library_preferences.json")

DEFAULT_PREFERENCES = {
    "library_name": "The Lembo Library",
    "default_room": "Office",
    "shelf_sort": "Author",
    "read_not_owned_position": "Last",
}


def load_preferences():
    preferences = DEFAULT_PREFERENCES.copy()
    if PREFERENCES_PATH.exists():
        try:
            saved = json.loads(PREFERENCES_PATH.read_text(encoding="utf-8"))
            preferences.update({key: saved[key] for key in preferences if key in saved})
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return preferences


def save_preferences(preferences):
    saved = DEFAULT_PREFERENCES.copy()
    saved.update({key: preferences[key] for key in saved if key in preferences})
    PREFERENCES_PATH.write_text(
        json.dumps(saved, indent=2) + "\n",
        encoding="utf-8"
    )
