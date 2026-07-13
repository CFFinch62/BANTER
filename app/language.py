"""Plugin surface a language-specific IDE implements to hook into Base IDE.

To add a language: subclass LanguageProvider, then in MainWindow.__init__
replace `self.language_provider = PlainTextLanguageProvider()` with an
instance of your subclass.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtGui import QSyntaxHighlighter, QTextDocument
from PyQt6.QtWidgets import QWidget

from app.themes import SyntaxColors

if TYPE_CHECKING:
    from app.terminal import TerminalPane


class LanguageProvider(ABC):
    """Base class for plugging a language into the Base IDE shell."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name, e.g. 'Python'. Shown as the editor's language label."""

    @property
    def file_extensions(self) -> List[str]:
        """File extensions this provider handles, e.g. ['.py']. Empty means no association."""
        return []

    def create_highlighter(
        self, document: QTextDocument, syntax_colors: SyntaxColors
    ) -> Optional[QSyntaxHighlighter]:
        """Return a QSyntaxHighlighter attached to `document`, or None for plain text."""
        return None

    def create_toolbar_widget(self, parent: QWidget) -> Optional[QWidget]:
        """Return an optional widget added to the toolbar (e.g. a runtime/backend picker)."""
        return None

    @abstractmethod
    def run(self, source: str, terminal: "TerminalPane") -> None:
        """Execute `source` (the active editor's full text), writing output to `terminal`."""

    def handle_input(self, text: str, terminal: "TerminalPane") -> None:
        """Handle a line typed into the console's input field (e.g. forward to a REPL)."""
        terminal.write(f"> {text}")


class PlainTextLanguageProvider(LanguageProvider):
    """Default provider used by the unmodified skeleton: no execution, no highlighting."""

    @property
    def name(self) -> str:
        return "Plain Text"

    def run(self, source: str, terminal: "TerminalPane") -> None:
        terminal.write(source)
        terminal.write("\n[Execution placeholder: implement LanguageProvider.run() for your language]\n")
