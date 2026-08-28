"""Tabbed reference-document reader panel.

Renders plain text, Markdown, and HTML files from the project's docs/
directory. Sits as a top-level, always-full-height, independently
resizable column at the right of the main window — a sibling of the
file browser and the editor/console splitter, not nested inside either.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QTabWidget, QTextBrowser, QVBoxLayout, QWidget

DOC_EXTENSIONS = {".md", ".markdown", ".txt", ".html", ".htm"}


def default_docs_dir() -> Path:
    """The project's docs/ directory: bundled next to app/ at the project
    root, or under sys._MEIPASS when frozen by PyInstaller (see build.py's
    --add-data entry for this folder)."""
    app_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return app_root / "docs"


class _DocBrowser(QTextBrowser):
    """QTextBrowser tagged with the doc file it's displaying, so DocPanel
    can find an already-open tab instead of opening a duplicate."""

    def __init__(self, doc_path: Path, parent=None):
        super().__init__(parent)
        self.doc_path = doc_path


class DocPanel(QWidget):
    """Tabbed viewer for reference documents staged in docs_dir."""

    def __init__(self, docs_dir: Optional[Path] = None, parent=None):
        super().__init__(parent)
        self.docs_dir = docs_dir or default_docs_dir()
        self._theme = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        layout.addWidget(self.tabs)

    def open_doc(self, path: Path) -> None:
        """Open `path` in a new tab, or focus its tab if already open."""
        path = Path(path)
        for index in range(self.tabs.count()):
            browser = self.tabs.widget(index)
            if isinstance(browser, _DocBrowser) and browser.doc_path == path:
                self.tabs.setCurrentIndex(index)
                return

        browser = _DocBrowser(path, self)
        browser.setOpenLinks(False)
        browser.setOpenExternalLinks(False)
        browser.anchorClicked.connect(lambda url, b=browser: self._on_anchor_clicked(url, b))
        self._render(browser, path)
        if self._theme is not None:
            self._apply_theme_to_browser(browser, self._theme)

        index = self.tabs.addTab(browser, path.name)
        self.tabs.setCurrentIndex(index)

    def _render(self, browser: QTextBrowser, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            browser.setPlainText(f"Could not load {path.name}: {exc}")
            return
        browser.setSearchPaths([str(path.parent)])
        suffix = path.suffix.lower()
        if suffix in (".md", ".markdown"):
            browser.setMarkdown(text)
        elif suffix in (".html", ".htm"):
            browser.setHtml(text)
        else:
            browser.setPlainText(text)

    def _close_tab(self, index: int) -> None:
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if widget is not None:
            widget.deleteLater()

    def _on_anchor_clicked(self, url: QUrl, browser: "_DocBrowser") -> None:
        if not url.scheme() or url.scheme() == "file":
            target = self.docs_dir / Path(url.path()).name
            if target.exists():
                self.open_doc(target)
                return
        QDesktopServices.openUrl(url)

    def apply_theme(self, theme) -> None:
        self._theme = theme
        self.tabs.setStyleSheet(
            f"QTabWidget::pane {{ border: 1px solid {theme.panel_border}; background-color: {theme.editor_background}; }}"
            f"QTabBar::tab {{ background-color: {theme.panel_background}; color: {theme.foreground}; border: 1px solid {theme.panel_border}; padding: 6px 8px; }}"
            f"QTabBar::tab:selected {{ background-color: {theme.editor_background}; color: {theme.accent}; }}"
        )
        for index in range(self.tabs.count()):
            browser = self.tabs.widget(index)
            if isinstance(browser, QTextBrowser):
                self._apply_theme_to_browser(browser, theme)

    def _apply_theme_to_browser(self, browser: QTextBrowser, theme) -> None:
        browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {theme.editor_background}; color: {theme.foreground}; border: none; }}"
        )
