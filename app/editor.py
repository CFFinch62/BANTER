from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QSyntaxHighlighter,
    QTextCursor,
    QTextDocument,
    QTextFormat,
)
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from app.themes import SyntaxColors

if TYPE_CHECKING:
    from app.language import LanguageProvider


class _LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor"):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        self._editor.paint_line_number_area(event)


class CodeEditor(QPlainTextEdit):
    """Simple, language-agnostic editor widget for the IDE skeleton."""

    def __init__(self, parent=None, file_path: Optional[Path] = None):
        super().__init__(parent)
        self.file_path: Optional[Path] = Path(file_path) if file_path else None
        self.language_name = "Plain Text"
        self._dirty = False
        self._theme = None
        self._highlighter: Optional[QSyntaxHighlighter] = None

        font = QFont("JetBrains Mono", 11)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(4 * QFontMetrics(font).horizontalAdvance(" "))
        self.setCenterOnScroll(False)

        self.textChanged.connect(self._mark_dirty)

        self._line_number_area = _LineNumberArea(self)
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self._update_line_number_area_width()
        self._highlight_current_line()

    def _mark_dirty(self) -> None:
        self._dirty = True

    def set_initial_text(self, text: str) -> None:
        """Set starting content (e.g. a new-tab template) without marking the editor dirty."""
        self.setPlainText(text)
        self._dirty = False

    def load_from_file(self, path: Path) -> None:
        self.file_path = path
        self.setPlainText(path.read_text(encoding="utf-8"))
        self._dirty = False

    def save_to_file(self, path: Optional[Path] = None) -> None:
        target = path or self.file_path
        if target is None:
            raise ValueError("No target path available for save")
        target.write_text(self.toPlainText(), encoding="utf-8")
        self.file_path = target
        self._dirty = False

    def is_dirty(self) -> bool:
        return self._dirty

    def set_language(self, language_name: str) -> None:
        self.language_name = language_name

    def set_language_provider(self, provider: "LanguageProvider") -> None:
        """Wire this editor up to a LanguageProvider's syntax highlighting."""
        self.language_name = provider.name
        if self._highlighter is not None:
            self._highlighter.setDocument(None)
            self._highlighter = None
        syntax_colors = self._theme.syntax if self._theme is not None else SyntaxColors()
        self._highlighter = provider.create_highlighter(self.document(), syntax_colors)

    # -- Find / Replace -------------------------------------------------

    def find_text(self, text: str, backward: bool = False, case_sensitive: bool = False) -> bool:
        if not text:
            return False
        flags = QTextDocument.FindFlag(0)
        if backward:
            flags |= QTextDocument.FindFlag.FindBackward
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        found = self.document().find(text, self.textCursor(), flags)
        if found.isNull():
            wrap_cursor = QTextCursor(self.document())
            if backward:
                wrap_cursor.movePosition(QTextCursor.MoveOperation.End)
            found = self.document().find(text, wrap_cursor, flags)
        if found.isNull():
            return False
        self.setTextCursor(found)
        return True

    def replace_current(self, find: str, replace: str, case_sensitive: bool = False) -> bool:
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            matches = selected == find if case_sensitive else selected.lower() == find.lower()
            if matches:
                cursor.insertText(replace)
                return True
        return self.find_text(find, case_sensitive=case_sensitive)

    def replace_all(self, find: str, replace: str, case_sensitive: bool = False) -> int:
        if not find:
            return 0
        flags = QTextDocument.FindFlag.FindCaseSensitively if case_sensitive else QTextDocument.FindFlag(0)
        edit_cursor = self.textCursor()
        edit_cursor.beginEditBlock()
        search_cursor = QTextCursor(self.document())
        count = 0
        while True:
            search_cursor = self.document().find(find, search_cursor, flags)
            if search_cursor.isNull():
                break
            search_cursor.insertText(replace)
            count += 1
        edit_cursor.endEditBlock()
        return count

    # -- Line number gutter -----------------------------------------------

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_number_area_width(self, _: int = 0) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def paint_line_number_area(self, event) -> None:
        painter = QPainter(self._line_number_area)
        bg = QColor(self._theme.editor_gutter_bg) if self._theme is not None else QColor("#181825")
        fg = QColor(self._theme.editor_gutter_fg) if self._theme is not None else QColor("#6c7086")
        painter.fillRect(event.rect(), bg)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        painter.setFont(self.font())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(fg)
                painter.drawText(
                    0,
                    top,
                    self._line_number_area.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def _highlight_current_line(self) -> None:
        selection = QTextEdit.ExtraSelection()
        color = QColor(self._theme.editor_line_highlight) if self._theme is not None else QColor("#2a2a3c")
        selection.format.setBackground(color)
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    def apply_theme(self, theme) -> None:
        self._theme = theme
        self.setStyleSheet(
            f"QPlainTextEdit {{ background-color: {theme.editor_background}; color: {theme.editor_foreground}; }}"
        )
        self.setCursorWidth(2)
        self.setBackgroundVisible(True)
        self.setCenterOnScroll(False)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(theme.editor_background))
        palette.setColor(self.foregroundRole(), QColor(theme.editor_foreground))
        self.setPalette(palette)

        self.setPlaceholderText("")
        self._highlight_current_line()
        self._line_number_area.update()
        if self._highlighter is not None and hasattr(self._highlighter, "set_colors"):
            self._highlighter.set_colors(theme.syntax)
