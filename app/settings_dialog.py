"""
Preferences dialog for BANTER.
Lets the user configure editor/console fonts, colors, and behavior.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSpinBox, QCheckBox, QComboBox, QPushButton,
    QGroupBox, QFormLayout, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QFontComboBox, QColorDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from app.settings import SettingsManager
from app.themes import ThemeManager


SHORTCUTS = [
    ("File", "New File", "Ctrl+N"),
    ("File", "Open File", "Ctrl+O"),
    ("File", "Save", "Ctrl+S"),
    ("File", "Save As", "Ctrl+Shift+S"),
    ("File", "Exit", "Ctrl+Q"),
    ("Edit", "Undo", "Ctrl+Z"),
    ("Edit", "Redo", "Ctrl+Shift+Z"),
    ("Edit", "Cut", "Ctrl+X"),
    ("Edit", "Copy", "Ctrl+C"),
    ("Edit", "Paste", "Ctrl+V"),
    ("Edit", "Find / Replace", "Ctrl+F"),
    ("Edit", "Indent Selection", "Tab"),
    ("Edit", "Dedent Selection", "Shift+Tab"),
    ("Edit", "Comment Selection", "Ctrl+/"),
    ("Edit", "Preferences", "Ctrl+,"),
    ("View", "Toggle File Browser", "Ctrl+B"),
    ("View", "Toggle Console", "Ctrl+`"),
    ("Run", "Run", "F5"),
]


class SettingsDialog(QDialog):
    """Preferences dialog for IDE settings"""

    settings_applied = pyqtSignal()

    def __init__(self, settings: SettingsManager, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings
        self.theme_manager = theme_manager
        self.setWindowTitle("Preferences")
        self.setMinimumSize(460, 420)
        self._console_fg_override = ""
        self._console_bg_override = ""
        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_editor_tab(), "Editor")
        self.tabs.addTab(self._create_console_tab(), "Console")
        self.tabs.addTab(self._create_theme_tab(), "Theme")
        self.tabs.addTab(self._create_shortcuts_tab(), "Shortcuts")
        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_settings)
        btn_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._ok_clicked)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _create_editor_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        font_group = QGroupBox("Font")
        font_layout = QFormLayout()

        self.font_family_input = QFontComboBox()
        self.font_family_input.setFontFilters(QFontComboBox.FontFilter.MonospacedFonts)
        font_layout.addRow("Font Family:", self.font_family_input)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 32)
        font_layout.addRow("Font Size:", self.font_size_spin)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        tab_row = QHBoxLayout()
        tab_row.addWidget(QLabel("Tab Width:"))
        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setRange(2, 8)
        tab_row.addWidget(self.tab_width_spin)
        tab_row.addStretch()
        behavior_layout.addLayout(tab_row)

        self.word_wrap_check = QCheckBox("Word Wrap")
        behavior_layout.addWidget(self.word_wrap_check)

        self.line_numbers_check = QCheckBox("Show Line Numbers")
        behavior_layout.addWidget(self.line_numbers_check)

        self.highlight_line_check = QCheckBox("Highlight Current Line")
        behavior_layout.addWidget(self.highlight_line_check)

        self.auto_indent_check = QCheckBox("Auto-Indent New Lines")
        behavior_layout.addWidget(self.auto_indent_check)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        layout.addStretch()
        return tab

    def _create_console_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        font_group = QGroupBox("Console Font")
        font_layout = QFormLayout()

        self.console_font_input = QFontComboBox()
        self.console_font_input.setFontFilters(QFontComboBox.FontFilter.MonospacedFonts)
        font_layout.addRow("Font Family:", self.console_font_input)

        self.console_font_size_spin = QSpinBox()
        self.console_font_size_spin.setRange(8, 24)
        font_layout.addRow("Font Size:", self.console_font_size_spin)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        color_group = QGroupBox("Console Colors")
        color_layout = QFormLayout()

        fg_row = QHBoxLayout()
        self.console_fg_swatch = QPushButton()
        self.console_fg_swatch.setFixedSize(32, 22)
        self.console_fg_swatch.clicked.connect(self._pick_console_fg_color)
        fg_row.addWidget(self.console_fg_swatch)
        fg_reset = QPushButton("Reset to Theme")
        fg_reset.clicked.connect(self._reset_console_fg_color)
        fg_row.addWidget(fg_reset)
        fg_row.addStretch()
        color_layout.addRow("Text Color:", fg_row)

        bg_row = QHBoxLayout()
        self.console_bg_swatch = QPushButton()
        self.console_bg_swatch.setFixedSize(32, 22)
        self.console_bg_swatch.clicked.connect(self._pick_console_bg_color)
        bg_row.addWidget(self.console_bg_swatch)
        bg_reset = QPushButton("Reset to Theme")
        bg_reset.clicked.connect(self._reset_console_bg_color)
        bg_row.addWidget(bg_reset)
        bg_row.addStretch()
        color_layout.addRow("Background Color:", bg_row)

        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        layout.addStretch()
        return tab

    def _create_theme_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        ui_theme_group = QGroupBox("UI Theme")
        ui_theme_layout = QVBoxLayout()

        self.ui_theme_combo = QComboBox()
        for name in self.theme_manager.available_themes():
            self.ui_theme_combo.addItem(name.replace("_", " ").title(), name)
        ui_theme_layout.addWidget(self.ui_theme_combo)

        ui_theme_group.setLayout(ui_theme_layout)
        layout.addWidget(ui_theme_group)

        layout.addStretch()
        return tab

    def _create_shortcuts_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Current keyboard shortcuts:"))

        tree = QTreeWidget()
        tree.setHeaderLabels(["Action", "Shortcut", "Category"])
        tree.setRootIsDecorated(False)
        tree.setAlternatingRowColors(True)
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        for category, action, shortcut in SHORTCUTS:
            tree.addTopLevelItem(QTreeWidgetItem([action, shortcut, category]))

        layout.addWidget(tree)
        return tab

    def _load_current_settings(self) -> None:
        s = self.settings_manager.settings

        self.font_family_input.setCurrentText(s.editor.font_family)
        self.font_size_spin.setValue(s.editor.font_size)
        self.tab_width_spin.setValue(s.editor.tab_width)
        self.word_wrap_check.setChecked(s.editor.word_wrap)
        self.line_numbers_check.setChecked(s.editor.show_line_numbers)
        self.highlight_line_check.setChecked(s.editor.highlight_current_line)
        self.auto_indent_check.setChecked(s.editor.auto_indent)

        self.console_font_input.setCurrentText(s.terminal.font_family)
        self.console_font_size_spin.setValue(s.terminal.font_size)
        self._console_fg_override = s.terminal.foreground_color
        self._console_bg_override = s.terminal.background_color
        self._update_console_swatches()

        theme_idx = self.ui_theme_combo.findData(self.theme_manager.current_theme_name())
        if theme_idx >= 0:
            self.ui_theme_combo.setCurrentIndex(theme_idx)

    def _current_terminal_theme_colors(self):
        theme_name = self.ui_theme_combo.currentData()
        theme = self.theme_manager.get_theme(theme_name) if theme_name else self.theme_manager.current_theme()
        return theme.terminal_foreground, theme.terminal_background

    def _update_console_swatches(self) -> None:
        default_fg, default_bg = self._current_terminal_theme_colors()
        fg = self._console_fg_override or default_fg
        bg = self._console_bg_override or default_bg
        self.console_fg_swatch.setStyleSheet(
            f"background-color: {fg}; border: 1px solid #00000040; border-radius: 3px;"
        )
        self.console_bg_swatch.setStyleSheet(
            f"background-color: {bg}; border: 1px solid #00000040; border-radius: 3px;"
        )

    def _pick_console_fg_color(self) -> None:
        default_fg, _ = self._current_terminal_theme_colors()
        current = QColor(self._console_fg_override or default_fg)
        chosen = QColorDialog.getColor(current, self, "Console Text Color")
        if chosen.isValid():
            self._console_fg_override = chosen.name()
            self._update_console_swatches()

    def _reset_console_fg_color(self) -> None:
        self._console_fg_override = ""
        self._update_console_swatches()

    def _pick_console_bg_color(self) -> None:
        _, default_bg = self._current_terminal_theme_colors()
        current = QColor(self._console_bg_override or default_bg)
        chosen = QColorDialog.getColor(current, self, "Console Background Color")
        if chosen.isValid():
            self._console_bg_override = chosen.name()
            self._update_console_swatches()

    def _reset_console_bg_color(self) -> None:
        self._console_bg_override = ""
        self._update_console_swatches()

    def _apply_settings(self) -> None:
        s = self.settings_manager.settings

        s.editor.font_family = self.font_family_input.currentText()
        s.editor.font_size = self.font_size_spin.value()
        s.editor.tab_width = self.tab_width_spin.value()
        s.editor.word_wrap = self.word_wrap_check.isChecked()
        s.editor.show_line_numbers = self.line_numbers_check.isChecked()
        s.editor.highlight_current_line = self.highlight_line_check.isChecked()
        s.editor.auto_indent = self.auto_indent_check.isChecked()

        s.terminal.font_family = self.console_font_input.currentText()
        s.terminal.font_size = self.console_font_size_spin.value()
        s.terminal.foreground_color = self._console_fg_override
        s.terminal.background_color = self._console_bg_override

        new_theme = self.ui_theme_combo.currentData()
        if new_theme:
            self.theme_manager.set_theme(new_theme)

        self.settings_manager.save()
        self.settings_applied.emit()

    def _ok_clicked(self) -> None:
        self._apply_settings()
        self.accept()
