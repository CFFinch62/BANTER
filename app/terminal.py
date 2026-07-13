from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget


class TerminalPane(QWidget):
    """Simple terminal/console panel for output and input."""

    command_entered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.setStyleSheet(
            f"QWidget {{ background-color: {theme.terminal_background}; color: {theme.terminal_foreground}; }}"
            f"QLabel {{ background-color: {theme.panel_background}; color: {theme.foreground}; "
            f"border-bottom: 1px solid {theme.panel_border}; font-weight: bold; }}"
            f"QLineEdit, QPlainTextEdit {{ background-color: {theme.terminal_background}; color: {theme.terminal_foreground}; border: 1px solid {theme.panel_border}; }}"
        )
        palette = self.output.palette()
        palette.setColor(self.output.backgroundRole(), QColor(theme.terminal_background))
        palette.setColor(self.output.foregroundRole(), QColor(theme.terminal_foreground))
        self.output.setPalette(palette)
        self.input_line.setPalette(palette)
