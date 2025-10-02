import json
from pathlib import Path


class SettingsManager:
    def __init__(self):
        self.settings_file = Path.home() / ".retention_pipeline" / "settings.json"
        self.settings_file.parent.mkdir(exist_ok=True)
    
    def load_settings(self):
        if not self.settings_file.exists():
            return self._get_default_settings()
        
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                return self._merge_with_defaults(settings)
        except (json.JSONDecodeError, IOError):
            return self._get_default_settings()
    
    def save_settings(self, settings):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except IOError:
            return False
    
    def has_api_key(self):
        settings = self.load_settings()
        api_key = settings.get("api_key", "").strip()
        return bool(api_key)
    
    def _get_default_settings(self):
        return {
            "api_key": "",
            "flashcards": {"enabled": True, "mode": "quick"}
        }
    
    def _merge_with_defaults(self, settings):
        defaults = self._get_default_settings()
        defaults.update(settings)
        
        if "flashcards" not in defaults:
            defaults["flashcards"] = {}
        defaults["flashcards"] = {**defaults["flashcards"], **self._get_default_settings()["flashcards"]}
        
        return defaults