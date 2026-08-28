from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget


class TerminalPane(QWidget):
    """Simple terminal/console panel for output and input."""

    command_entered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme = None
        self._fg_override = ""
        self._bg_override = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = QLabel("CONSOLE / TERMINAL")
        self.label.setContentsMargins(6, 3, 6, 3)
        layout.addWidget(self.label)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.output.setFont(QFont("JetBrains Mono", 10))
        layout.addWidget(self.output, stretch=1)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type here...")
        self.input_line.setMinimumHeight(32)
        self.input_line.returnPressed.connect(self._on_return_pressed)
        layout.addWidget(self.input_line)

    def apply_settings(self, settings) -> None:
        """Apply an app.settings.TerminalSettings to this console pane."""
        font = QFont(settings.font_family, settings.font_size)
        self.output.setFont(font)
        self.input_line.setFont(font)
        self._fg_override = settings.foreground_color
        self._bg_override = settings.background_color
        if self._theme is not None:
            self.apply_theme(self._theme)

    def _on_return_pressed(self) -> None:
        text = self.input_line.text()
        if not text:
            return
        self.input_line.clear()
        self.command_entered.emit(text)

    def write(self, text: str) -> None:
        self.output.appendPlainText(text)

    def clear(self) -> None:
        self.output.clear()

    def apply_theme(self, theme) -> None:
        self._theme = theme
        bg = self._bg_override or theme.terminal_background
        fg = self._fg_override or theme.terminal_foreground
        self.setStyleSheet(
            f"QWidget {{ background-color: {bg}; color: {fg}; }}"
            f"QLabel {{ background-color: {theme.panel_background}; color: {theme.foreground}; "
            f"border-bottom: 1px solid {theme.panel_border}; font-weight: bold; }}"
            f"QLineEdit, QPlainTextEdit {{ background-color: {bg}; color: {fg}; border: 1px solid {theme.panel_border}; }}"
        )
        palette = self.output.palette()
        palette.setColor(self.output.backgroundRole(), QColor(bg))
        palette.setColor(self.output.foregroundRole(), QColor(fg))
        self.output.setPalette(palette)
        self.input_line.setPalette(palette)
