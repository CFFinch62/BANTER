from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from PyQt6.QtCore import QObject, QSettings, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget


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

LIGHT_THEME = UITheme(
    name="Light",
    is_dark=False,
    background="#eff1f5",
    foreground="#4c4f69",
    accent="#1e66f5",
    accent_hover="#2a7afd",
    panel_background="#e6e9ef",
    panel_border="#bcc0cc",
    browser_background="#e6e9ef",
    browser_item_hover="#acb0be",
    browser_item_selected="#1e66f5",
    editor_background="#eff1f5",
    editor_foreground="#4c4f69",
    editor_line_highlight="#dce0e8",
    editor_selection="#acb0be",
    editor_gutter_bg="#e6e9ef",
    editor_gutter_fg="#8c8fa1",
    terminal_background="#dce0e8",
    terminal_foreground="#4c4f69",
    scrollbar_background="#e6e9ef",
    scrollbar_handle="#bcc0cc",
    scrollbar_handle_hover="#acb0be",
    button_background="#bcc0cc",
    button_foreground="#4c4f69",
    button_hover="#acb0be",
    button_pressed="#ccd0da",
    input_background="#ccd0da",
    input_border="#bcc0cc",
    input_focus_border="#1e66f5",
    success="#40a02b",
    warning="#df8e1d",
    error="#d20f39",
    info="#1e66f5",
    syntax=SyntaxColors(
        keyword="#1e66f5",
        builtin="#df8e1d",
        string="#40a02b",
        number="#fe640b",
        comment="#8c8fa1",
        literal="#179299",
        operator="#8839ef",
        identifier="#4c4f69",
    ),
)

GREY_THEME = UITheme(
    name="Grey",
    is_dark=True,
    background="#2b2d30",
    foreground="#bcbec4",
    accent="#4a9eff",
    accent_hover="#5eadff",
    panel_background="#25262a",
    panel_border="#3c3f41",
    browser_background="#25262a",
    browser_item_hover="#5a5d62",
    browser_item_selected="#4a9eff",
    editor_background="#2b2d30",
    editor_foreground="#bcbec4",
    editor_line_highlight="#323437",
    editor_selection="#214283",
    editor_gutter_bg="#25262a",
    editor_gutter_fg="#6c6f73",
    terminal_background="#1e1f22",
    terminal_foreground="#bcbec4",
    scrollbar_background="#25262a",
    scrollbar_handle="#4a5157",
    scrollbar_handle_hover="#5a5d62",
    button_background="#4a5157",
    button_foreground="#bcbec4",
    button_hover="#5a5d62",
    button_pressed="#3c3f41",
    input_background="#3c3f41",
    input_border="#4a5157",
    input_focus_border="#4a9eff",
    success="#6aab73",
    warning="#d5b778",
    error="#c75450",
    info="#4a9eff",
    syntax=SyntaxColors(
        keyword="#6897bb",
        builtin="#d5b778",
        string="#6a8759",
        number="#d19a66",
        comment="#6c6f73",
        literal="#6897bb",
        operator="#cc7832",
        identifier="#bcbec4",
    ),
)

SOLARIZED_LIGHT_THEME = UITheme(
    name="Solarized Light",
    is_dark=False,
    background="#fdf6e3",
    foreground="#657b83",
    accent="#268bd2",
    accent_hover="#2aa1f5",
    panel_background="#eee8d5",
    panel_border="#93a1a1",
    browser_background="#eee8d5",
    browser_item_hover="#839496",
    browser_item_selected="#268bd2",
    editor_background="#fdf6e3",
    editor_foreground="#657b83",
    editor_line_highlight="#eee8d5",
    editor_selection="#eee8d5",
    editor_gutter_bg="#eee8d5",
    editor_gutter_fg="#93a1a1",
    terminal_background="#eee8d5",
    terminal_foreground="#657b83",
    scrollbar_background="#eee8d5",
    scrollbar_handle="#93a1a1",
    scrollbar_handle_hover="#839496",
    button_background="#93a1a1",
    button_foreground="#fdf6e3",
    button_hover="#839496",
    button_pressed="#eee8d5",
    input_background="#eee8d5",
    input_border="#93a1a1",
    input_focus_border="#268bd2",
    success="#859900",
    warning="#b58900",
    error="#dc322f",
    info="#268bd2",
    syntax=SyntaxColors(
        keyword="#268bd2",
        builtin="#b58900",
        string="#859900",
        number="#cb4b16",
        comment="#93a1a1",
        literal="#2aa198",
        operator="#d33682",
        identifier="#657b83",
    ),
)

SOLARIZED_DARK_THEME = UITheme(
    name="Solarized Dark",
    is_dark=True,
    background="#002b36",
    foreground="#839496",
    accent="#268bd2",
    accent_hover="#2aa1f5",
    panel_background="#073642",
    panel_border="#586e75",
    browser_background="#073642",
    browser_item_hover="#657b83",
    browser_item_selected="#268bd2",
    editor_background="#002b36",
    editor_foreground="#839496",
    editor_line_highlight="#073642",
    editor_selection="#073642",
    editor_gutter_bg="#073642",
    editor_gutter_fg="#586e75",
    terminal_background="#073642",
    terminal_foreground="#839496",
    scrollbar_background="#073642",
    scrollbar_handle="#586e75",
    scrollbar_handle_hover="#657b83",
    button_background="#586e75",
    button_foreground="#fdf6e3",
    button_hover="#657b83",
    button_pressed="#073642",
    input_background="#073642",
    input_border="#586e75",
    input_focus_border="#268bd2",
    success="#859900",
    warning="#b58900",
    error="#dc322f",
    info="#268bd2",
    syntax=SyntaxColors(
        keyword="#268bd2",
        builtin="#b58900",
        string="#859900",
        number="#cb4b16",
        comment="#586e75",
        literal="#2aa198",
        operator="#d33682",
        identifier="#839496",
    ),
)

HIGH_CONTRAST_THEME = UITheme(
    name="High Contrast",
    is_dark=True,
    background="#000000",
    foreground="#ffffff",
    accent="#4fc3f7",
    accent_hover="#81d4fa",
    panel_background="#0a0a0a",
    panel_border="#444444",
    browser_background="#0a0a0a",
    browser_item_hover="#555555",
    browser_item_selected="#4fc3f7",
    editor_background="#000000",
    editor_foreground="#ffffff",
    editor_line_highlight="#1a1a1a",
    editor_selection="#264f78",
    editor_gutter_bg="#0a0a0a",
    editor_gutter_fg="#888888",
    terminal_background="#0a0a0a",
    terminal_foreground="#ffffff",
    scrollbar_background="#0a0a0a",
    scrollbar_handle="#555555",
    scrollbar_handle_hover="#777777",
    button_background="#333333",
    button_foreground="#ffffff",
    button_hover="#555555",
    button_pressed="#222222",
    input_background="#1a1a1a",
    input_border="#555555",
    input_focus_border="#4fc3f7",
    success="#00ff00",
    warning="#ffff00",
    error="#ff4444",
    info="#4fc3f7",
    syntax=SyntaxColors(
        keyword="#6dcfff",
        builtin="#ffd700",
        string="#00ff7f",
        number="#ff8c00",
        comment="#888888",
        literal="#00e5ff",
        operator="#ff69b4",
        identifier="#ffffff",
    ),
)

THEMES: Dict[str, UITheme] = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "grey": GREY_THEME,
    "solarized_light": SOLARIZED_LIGHT_THEME,
    "solarized_dark": SOLARIZED_DARK_THEME,
    "high_contrast": HIGH_CONTRAST_THEME,
}


class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("BaseIDE", "Base IDE")
        self._current_theme_name = self._load_saved_theme()
        self._current_theme = THEMES.get(self._current_theme_name, DARK_THEME)

    def available_themes(self) -> List[str]:
        return list(THEMES.keys())

    def current_theme(self) -> UITheme:
        return self._current_theme

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
        theme = self.current_theme()
        self._apply_theme_to_widget(widget, theme)
        for child in widget.findChildren(QWidget):
            self._apply_theme_to_widget(child, theme)

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
        saved = self._settings.value("theme", "dark")
        if isinstance(saved, str) and saved in THEMES:
            return saved
        return "dark"
