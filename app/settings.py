"""
Settings manager for BANTER.
Handles loading, saving, and managing user preferences.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List


def get_config_dir() -> Path:
    """Get the configuration directory for BANTER"""
    config_dir = Path.home() / ".config" / "banter_ide"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@dataclass
class EditorSettings:
    """Editor-specific settings"""
    font_family: str = "JetBrains Mono"
    font_size: int = 11
    tab_width: int = 4
    word_wrap: bool = False
    show_line_numbers: bool = True
    highlight_current_line: bool = True
    auto_indent: bool = True


@dataclass
class TerminalSettings:
    """Console/terminal panel settings"""
    font_family: str = "JetBrains Mono"
    font_size: int = 10
    # Empty string means "follow the current UI theme's terminal colors"
    foreground_color: str = ""
    background_color: str = ""


@dataclass
class FileBrowserSettings:
    """File browser settings"""
    bookmarks: List[str] = field(default_factory=list)


@dataclass
class Settings:
    """All IDE settings.

    UI theme is intentionally not stored here: ThemeManager already owns
    theme persistence via QSettings, so it stays the single source of truth
    rather than risking drift between two saved copies of the same choice.
    """
    editor: EditorSettings = field(default_factory=EditorSettings)
    terminal: TerminalSettings = field(default_factory=TerminalSettings)
    file_browser: FileBrowserSettings = field(default_factory=FileBrowserSettings)


class SettingsManager:
    """Manages loading and saving of settings"""

    def __init__(self):
        self.config_file = get_config_dir() / "settings.json"
        self.settings = self._load()

    def _load(self) -> Settings:
        """Load settings from file or create defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return self._dict_to_settings(data)
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")
        return Settings()

    def _dict_to_settings(self, data: dict) -> Settings:
        settings = Settings()
        if "editor" in data:
            settings.editor = EditorSettings(**{
                k: v for k, v in data["editor"].items()
                if k in EditorSettings.__dataclass_fields__
            })
        if "terminal" in data:
            settings.terminal = TerminalSettings(**{
                k: v for k, v in data["terminal"].items()
                if k in TerminalSettings.__dataclass_fields__
            })
        if "file_browser" in data:
            settings.file_browser = FileBrowserSettings(
                bookmarks=data["file_browser"].get("bookmarks", [])
            )
        return settings

    def save(self) -> None:
        """Save settings to file"""
        data = {
            "editor": asdict(self.settings.editor),
            "terminal": asdict(self.settings.terminal),
            "file_browser": asdict(self.settings.file_browser),
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
