from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtCore import QObject, QSettings, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget

from app.settings import get_config_dir


@dataclass
class SyntaxColors:
    keyword: str = "#569cd6"
    builtin: str = "#e5a645"
    string: str = "#98c379"
    number: str = "#d19a66"
    comment: str = "#5c6370"
    literal: str = "#56b6c2"
    operator: str = "#c678dd"
    identifier: str = "#abb2bf"


@dataclass
class UITheme:
    name: str
    is_dark: bool
    background: str
    foreground: str
    accent: str
    accent_hover: str
    panel_background: str
    panel_border: str
    browser_background: str
    browser_item_hover: str
    browser_item_selected: str
    editor_background: str
    editor_foreground: str
    editor_line_highlight: str
    editor_selection: str
    editor_gutter_bg: str
    editor_gutter_fg: str
    terminal_background: str
    terminal_foreground: str
    scrollbar_background: str
    scrollbar_handle: str
    scrollbar_handle_hover: str
    button_background: str
    button_foreground: str
    button_hover: str
    button_pressed: str
    input_background: str
    input_border: str
    input_focus_border: str
    success: str
    warning: str
    error: str
    info: str
    syntax: SyntaxColors = field(default_factory=SyntaxColors)
    scope_depth_colors: List[str] = field(default_factory=lambda: ["#f9c74f", "#577590", "#90be6d", "#9b5de5"])


DARK_THEME = UITheme(
    name="Dark",
    is_dark=True,
    background="#1e1e2e",
    foreground="#cdd6f4",
    accent="#89b4fa",
    accent_hover="#74c7ec",
    panel_background="#181825",
    panel_border="#313244",
    browser_background="#181825",
    browser_item_hover="#585b70",
    browser_item_selected="#89b4fa",
    editor_background="#1e1e2e",
    editor_foreground="#cdd6f4",
    editor_line_highlight="#2a2a3c",
    editor_selection="#44475a",
    editor_gutter_bg="#181825",
    editor_gutter_fg="#6c7086",
    terminal_background="#11111b",
    terminal_foreground="#cdd6f4",
    scrollbar_background="#181825",
    scrollbar_handle="#45475a",
    scrollbar_handle_hover="#585b70",
    button_background="#45475a",
    button_foreground="#cdd6f4",
    button_hover="#585b70",
    button_pressed="#313244",
    input_background="#313244",
    input_border="#45475a",
    input_focus_border="#89b4fa",
    success="#a6e3a1",
    warning="#f9e2af",
    error="#f38ba8",
    info="#89b4fa",
    syntax=SyntaxColors(
        keyword="#89b4fa",
        builtin="#f9e2af",
        string="#a6e3a1",
        number="#fab387",
        comment="#6c7086",
        literal="#94e2d5",
        operator="#cba6f7",
        identifier="#cdd6f4",
    ),
)

_THEMES_DIRNAME = "themes"


def _bundled_themes_dir() -> Path:
    """Directory containing the shipped theme JSON files.

    PyInstaller extracts --add-data assets into sys._MEIPASS at runtime;
    when running from source, themes/ sits next to app/ at the project root.
    """
    app_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return app_root / _THEMES_DIRNAME


def _user_themes_dir() -> Path:
    """Directory for user-authored/dropped-in theme files, alongside settings.json."""
    return get_config_dir() / _THEMES_DIRNAME


def _theme_from_dict(data: dict, fallback: UITheme) -> UITheme:
    """Build a UITheme from a parsed JSON dict, filling any missing field
    (or an entirely missing/invalid file) from `fallback` so a partial or
    stale theme file degrades gracefully instead of crashing the app."""
    fallback_dict = asdict(fallback)
    syntax_data = data.get("syntax") or {}
    fallback_syntax = fallback_dict["syntax"]
    syntax = SyntaxColors(**{
        key: syntax_data.get(key, default) for key, default in fallback_syntax.items()
    })

    kwargs = {
        key: data.get(key, default)
        for key, default in fallback_dict.items()
        if key != "syntax"
    }
    kwargs["syntax"] = syntax
    return UITheme(**kwargs)


def _load_theme_file(path: Path, fallback: UITheme) -> Optional[UITheme]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Warning: could not load theme {path}: {exc}")
        return None
    data.setdefault("name", path.stem.replace("_", " ").title())
    try:
        return _theme_from_dict(data, fallback)
    except (TypeError, ValueError) as exc:
        print(f"Warning: invalid theme {path}: {exc}")
        return None


def _discover_theme_files() -> List[Path]:
    files: List[Path] = []
    bundled_dir = _bundled_themes_dir()
    if bundled_dir.is_dir():
        files.extend(sorted(bundled_dir.glob("*.json")))
    user_dir = _user_themes_dir()
    if user_dir.is_dir():
        files.extend(sorted(user_dir.glob("*.json")))
    return files


def _build_theme_registry() -> Dict[str, UITheme]:
    """Load every theme JSON file (bundled, then user overrides/additions —
    a user file with the same filename stem as a bundled one wins) into a
    {slug: UITheme} registry. Falls back to the hardcoded DARK_THEME if no
    theme file loads at all, so the app can never end up with zero themes."""
    registry: Dict[str, UITheme] = {}
    for path in _discover_theme_files():
        theme = _load_theme_file(path, DARK_THEME)
        if theme is not None:
            registry[path.stem] = theme
    if not registry:
        registry["dark"] = DARK_THEME
    return registry


THEMES: Dict[str, UITheme] = _build_theme_registry()


class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("BanterIDE", "Banter IDE")
        self._current_theme_name = self._load_saved_theme()
        self._current_theme = THEMES.get(self._current_theme_name, DARK_THEME)

    def available_themes(self) -> List[str]:
        return list(THEMES.keys())

    def current_theme(self) -> UITheme:
        return self._current_theme

    def get_theme(self, name: str) -> UITheme:
        return THEMES.get(name, self._current_theme)

    def current_theme_name(self) -> str:
        return self._current_theme_name

    def set_theme(self, name: str) -> None:
        if name not in THEMES:
            return
        self._current_theme_name = name
        self._current_theme = THEMES[name]
        self._settings.setValue("theme", name)
        self.theme_changed.emit(name)

    def apply_to_widget(self, widget: QWidget | None) -> None:
        if widget is None:
            return
        self._apply_recursive(widget, self.current_theme())

    def _apply_recursive(self, widget: QWidget, theme: UITheme) -> None:
        """Depth-first theme walk that stops descending once it reaches a
        widget with its own apply_theme() — that widget owns styling for
        its whole subtree, so a widget like TerminalPane or DocPanel can
        rely on its own children (a QLineEdit, a QTextBrowser tab, ...)
        never getting silently re-stamped with the generic stylesheet
        afterwards. Using findChildren's default recursive search here
        instead would flatten the whole tree and defeat that boundary.
        """
        self._apply_theme_to_widget(widget, theme)
        if hasattr(widget, "apply_theme"):
            return
        for child in widget.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly):
            self._apply_recursive(child, theme)

    def _apply_theme_to_widget(self, widget: QWidget, theme: UITheme) -> None:
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(theme.background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme.foreground))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme.editor_background))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme.panel_background))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme.panel_background))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme.foreground))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme.foreground))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme.button_background))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme.button_foreground))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme.browser_item_selected))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme.background))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)

        if hasattr(widget, "apply_theme"):
            widget.apply_theme(theme)
            return

        widget.setStyleSheet(self._build_stylesheet(theme))

    def _build_stylesheet(self, theme: UITheme) -> str:
        return f"""
        QWidget {{ background-color: {theme.background}; color: {theme.foreground}; }}
        QMainWindow, QDockWidget {{ background-color: {theme.background}; color: {theme.foreground}; }}
        QSplitter::handle {{ background-color: {theme.panel_border}; }}
        QTabWidget::pane {{ border: 1px solid {theme.panel_border}; background-color: {theme.background}; }}
        QTabBar::tab {{ background-color: {theme.panel_background}; color: {theme.foreground}; border: 1px solid {theme.panel_border}; padding: 6px 8px; }}
        QTabBar::tab:selected {{ background-color: {theme.editor_background}; color: {theme.accent}; }}
        QToolBar {{ background-color: {theme.panel_background}; border: 1px solid {theme.panel_border}; spacing: 4px; }}
        QToolButton, QPushButton {{ background-color: {theme.button_background}; color: {theme.button_foreground}; border: 1px solid {theme.input_border}; padding: 4px 8px; }}
        QToolButton:hover, QPushButton:hover {{ background-color: {theme.button_hover}; }}
        QToolButton:pressed, QPushButton:pressed {{ background-color: {theme.button_pressed}; }}
        QLineEdit, QPlainTextEdit, QTextEdit, QListWidget, QTreeView, QStatusBar, QMenu, QComboBox {{ background-color: {theme.panel_background}; color: {theme.foreground}; border: 1px solid {theme.input_border}; }}
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus {{ border: 1px solid {theme.input_focus_border}; }}
        QTreeView::item:hover, QListWidget::item:hover {{ background-color: {theme.browser_item_hover}; }}
        QTreeView::item:selected, QListWidget::item:selected {{ background-color: {theme.browser_item_selected}; color: {theme.background}; }}
        QMenu::item:selected {{ background-color: {theme.browser_item_selected}; color: {theme.background}; }}
        QScrollBar:vertical, QScrollBar:horizontal {{ background: {theme.scrollbar_background}; }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{ background: {theme.scrollbar_handle}; border-radius: 4px; }}
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{ background: {theme.scrollbar_handle_hover}; }}
        QStatusBar {{ background-color: {theme.panel_background}; color: {theme.foreground}; }}
        """

    def _load_saved_theme(self) -> str:
        default_name = "dark" if "dark" in THEMES else next(iter(THEMES))
        saved = self._settings.value("theme", default_name)
        if isinstance(saved, str) and saved in THEMES:
            return saved
        return default_name
