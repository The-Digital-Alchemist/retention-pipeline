import json
from pathlib import Path

from ..validation import sanitize_api_key


class SettingsManager:
    def __init__(self):
        self.settings_file = Path.home() / ".retention_pipeline" / "settings.json"
        self.settings_file.parent.mkdir(exist_ok=True)

    def load_settings(self):
        if not self.settings_file.exists():
            return self._get_default_settings()

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                raw_settings = json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._get_default_settings()

        merged = self._merge_with_defaults(raw_settings)
        sanitized_key = sanitize_api_key(merged.get("api_key", ""))
        if sanitized_key != merged.get("api_key", ""):
            merged["api_key"] = sanitized_key
            # Persist the sanitized value so we don't have to clean it again later
            self.save_settings(merged)
        else:
            merged["api_key"] = sanitized_key

        return merged

    def save_settings(self, settings):
        merged = self._merge_with_defaults(settings)
        merged["api_key"] = sanitize_api_key(merged.get("api_key", ""))

        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(merged, f, indent=2)
            return True
        except IOError:
            return False

    def has_api_key(self):
        settings = self.load_settings()
        api_key = sanitize_api_key(settings.get("api_key", ""))
        return bool(api_key)

    def _get_default_settings(self):
        return {
            "api_key": "",
            "flashcards": {"enabled": True, "mode": "quick"},
        }

    def _merge_with_defaults(self, settings):
        defaults = self._get_default_settings()
        defaults.update(settings or {})

        if "flashcards" not in defaults:
            defaults["flashcards"] = {}
        defaults["flashcards"] = {
            **self._get_default_settings()["flashcards"],
            **defaults["flashcards"],
        }

        return defaults
