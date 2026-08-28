from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QActionGroup, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.editor import CodeEditor
from app.file_browser import FileBrowserWidget
from app.find_replace import FindReplaceDialog
from app.language import LanguageProvider
from app.smalltalk_language import SmalltalkLanguageProvider
from app.terminal import TerminalPane
from app.doc_panel import DOC_EXTENSIONS, DocPanel
from app.settings import SettingsManager
from app.settings_dialog import SettingsDialog
from app.themes import ThemeManager


class MainWindow(QMainWindow):
    """Generic IDE shell with menu, toolbar, file browser, editors, and console."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Banter IDE")
        self.theme_manager = ThemeManager(self)
        self.language_provider: LanguageProvider = SmalltalkLanguageProvider()
        self._settings = QSettings("BanterIDE", "Banter IDE")
        self.settings_manager = SettingsManager()
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_connections()
        self._apply_theme(self.theme_manager.current_theme_name())
        self._create_new_tab()
        self.resize(1400, 900)
        self._restore_window_state()

    def _setup_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)

        self.file_browser = FileBrowserWidget(self, self.settings_manager)
        self.file_browser.setMinimumWidth(260)
        self.file_browser.request_open.connect(self._open_file_path)
        self.splitter.addWidget(self.file_browser)

        self.content_splitter = QSplitter(Qt.Orientation.Vertical)
        self.content_splitter.setChildrenCollapsible(False)

        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.content_splitter.addWidget(self.tabs)

        self.terminal = TerminalPane(self)
        self.terminal.setMinimumHeight(160)
        self.terminal.apply_settings(self.settings_manager.settings.terminal)
        self.content_splitter.addWidget(self.terminal)

        self.splitter.addWidget(self.content_splitter)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.doc_panel = DocPanel(parent=self)
        self.doc_panel.setMinimumWidth(260)
        self.doc_panel.hide()
        self.splitter.addWidget(self.doc_panel)
        self.splitter.setStretchFactor(2, 0)

        self.find_replace_dialog = FindReplaceDialog(self)

    def _setup_menus(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        new_action = file_menu.addAction("&New")
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._create_new_tab)

        open_action = file_menu.addAction("&Open...")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file_dialog)

        save_action = file_menu.addAction("&Save")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_current_file)

        save_as_action = file_menu.addAction("Save &As...")
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_current_file_as)

        file_menu.addSeparator()
        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)

        edit_menu = menubar.addMenu("&Edit")

        undo_action = edit_menu.addAction("&Undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)

        redo_action = edit_menu.addAction("&Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)

        edit_menu.addSeparator()

        cut_action = edit_menu.addAction("Cu&t")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self._cut)

        copy_action = edit_menu.addAction("&Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._copy)

        paste_action = edit_menu.addAction("&Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._paste)

        edit_menu.addSeparator()

        find_action = edit_menu.addAction("&Find / Replace...")
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._open_find_replace)

        edit_menu.addSeparator()

        indent_action = edit_menu.addAction("&Indent Selection")
        indent_action.setShortcut("Ctrl+]")
        indent_action.triggered.connect(self._indent_selection)

        dedent_action = edit_menu.addAction("&Dedent Selection")
        dedent_action.setShortcut("Ctrl+[")
        dedent_action.triggered.connect(self._dedent_selection)

        comment_action = edit_menu.addAction("Co&mment Selection")
        comment_action.setShortcut("Ctrl+/")
        comment_action.triggered.connect(self._comment_selection)

        edit_menu.addSeparator()

        prefs_action = edit_menu.addAction("&Preferences...")
        prefs_action.setShortcut("Ctrl+,")
        prefs_action.triggered.connect(self._show_preferences)

        view_menu = menubar.addMenu("&View")
        self.toggle_browser_action = view_menu.addAction("Toggle File Browser")
        self.toggle_browser_action.setCheckable(True)
        self.toggle_browser_action.setChecked(True)
        self.toggle_browser_action.toggled.connect(self.file_browser.setVisible)

        self.toggle_terminal_action = view_menu.addAction("Toggle Console")
        self.toggle_terminal_action.setCheckable(True)
        self.toggle_terminal_action.setChecked(True)
        self.toggle_terminal_action.toggled.connect(self.terminal.setVisible)

        view_menu.addSeparator()
        console_position_group = QActionGroup(self)
        console_position_group.setExclusive(True)
        self.console_below_action = view_menu.addAction("Console Below Editor")
        self.console_below_action.setCheckable(True)
        self.console_below_action.setChecked(True)
        console_position_group.addAction(self.console_below_action)
        self.console_below_action.triggered.connect(lambda checked: self._set_console_position("bottom") if checked else None)

        self.console_right_action = view_menu.addAction("Console on Right")
        self.console_right_action.setCheckable(True)
        console_position_group.addAction(self.console_right_action)
        self.console_right_action.triggered.connect(lambda checked: self._set_console_position("right") if checked else None)

        view_menu.addSeparator()
        self.toggle_docs_action = view_menu.addAction("Toggle Documentation")
        self.toggle_docs_action.setCheckable(True)
        self.toggle_docs_action.setChecked(False)
        self.toggle_docs_action.toggled.connect(self.doc_panel.setVisible)

        theme_menu = menubar.addMenu("&Theme")
        self.theme_actions = {}
        for theme_name in self.theme_manager.available_themes():
            action = theme_menu.addAction(theme_name.replace("_", " ").title())
            action.setCheckable(True)
            action.triggered.connect(lambda checked, name=theme_name: self._set_theme(name))
            self.theme_actions[theme_name] = action
        self._update_theme_menu_selection()

        help_menu = menubar.addMenu("&Help")
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self._show_about)

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        toolbar.addAction("New", self._create_new_tab)
        toolbar.addAction("Open", self._open_file_dialog)
        toolbar.addAction("Save", self._save_current_file)
        toolbar.addSeparator()
        toolbar.addAction("Run", self._run_code)
        toolbar.addAction("Clear Console", self.terminal.clear)

        extra_widget = self.language_provider.create_toolbar_widget(toolbar)
        if extra_widget is not None:
            toolbar.addSeparator()
            toolbar.addWidget(extra_widget)

    def _setup_statusbar(self) -> None:
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")
        self.cursor_position_label = QLabel("")
        self.status.addPermanentWidget(self.cursor_position_label)

    def _setup_connections(self) -> None:
        self.theme_manager.theme_changed.connect(self._apply_theme)
        self.terminal.command_entered.connect(self._on_terminal_command)

    def _create_new_tab(self) -> None:
        editor = CodeEditor(self)
        self._apply_theme_to_widget(editor)
        editor.set_language_provider(self.language_provider)
        editor.apply_settings(self.settings_manager.settings.editor)
        editor.cursorPositionChanged.connect(self._update_cursor_position)
        editor.set_initial_text('"Start typing here"\n')
        index = self.tabs.addTab(editor, "untitled.st")
        self.tabs.setCurrentIndex(index)
        self._update_title()

    def _current_editor(self) -> Optional[CodeEditor]:
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, CodeEditor) else None

    def _open_file_path(self, path: str) -> None:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            self._open_path(file_path)

    def _open_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if path:
            self._open_path(Path(path))

    def _open_path(self, path: Path) -> None:
        """Route a file to the doc panel if it's a supported doc type staged
        under docs/, otherwise open it as a normal editor tab."""
        if self._is_doc_file(path):
            self._open_doc(path)
        else:
            self._open_file(path)

    def _is_doc_file(self, path: Path) -> bool:
        if path.suffix.lower() not in DOC_EXTENSIONS:
            return False
        try:
            path.resolve().relative_to(self.doc_panel.docs_dir.resolve())
        except ValueError:
            return False
        return True

    def _open_doc(self, path: Path) -> None:
        self.doc_panel.open_doc(path)
        self.doc_panel.setVisible(True)
        self.toggle_docs_action.setChecked(True)

    def _open_file(self, path: Path) -> None:
        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)
            if isinstance(editor, CodeEditor) and editor.file_path == path:
                self.tabs.setCurrentIndex(index)
                return

        editor = CodeEditor(self, file_path=path)
        self._apply_theme_to_widget(editor)
        editor.set_language_provider(self.language_provider)
        editor.apply_settings(self.settings_manager.settings.editor)
        editor.cursorPositionChanged.connect(self._update_cursor_position)
        try:
            editor.load_from_file(path)
        except OSError as exc:
            QMessageBox.critical(self, "Open File", f"Could not open {path}:\n{exc}")
            editor.deleteLater()
            return
        name = path.name or "untitled"
        self.tabs.addTab(editor, name)
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        self._update_title()

    def _save_current_file(self) -> None:
        editor = self._current_editor()
        if editor is None:
            return
        if editor.file_path is None:
            self._save_current_file_as()
            return
        try:
            editor.save_to_file(editor.file_path)
        except OSError as exc:
            QMessageBox.critical(self, "Save File", f"Could not save {editor.file_path}:\n{exc}")
            return
        self.tabs.setTabText(self.tabs.currentIndex(), editor.file_path.name)
        self.status.showMessage(f"Saved {editor.file_path}")

    def _save_current_file_as(self) -> None:
        editor = self._current_editor()
        if editor is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save File")
        if not path:
            return
        try:
            editor.save_to_file(Path(path))
        except OSError as exc:
            QMessageBox.critical(self, "Save File", f"Could not save {path}:\n{exc}")
            return
        self.tabs.setTabText(self.tabs.currentIndex(), Path(path).name)
        self.status.showMessage(f"Saved {path}")

    def _close_tab(self, index: int) -> None:
        widget = self.tabs.widget(index)
        if widget is None:
            return
        if isinstance(widget, CodeEditor) and widget.is_dirty():
            reply = QMessageBox.question(
                self,
                "Unsaved changes",
                "Close this tab without saving?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.tabs.removeTab(index)
        widget.deleteLater()
        self._update_title()

    def _on_tab_changed(self, index: int) -> None:
        self._update_title()
        self._update_cursor_position()
        self.find_replace_dialog.set_editor(self._current_editor())

    def _update_cursor_position(self) -> None:
        editor = self._current_editor()
        if editor is None:
            self.cursor_position_label.setText("")
            return
        cursor = editor.textCursor()
        self.cursor_position_label.setText(f"Ln {cursor.blockNumber() + 1}, Col {cursor.columnNumber() + 1}")

    def _open_find_replace(self) -> None:
        self.find_replace_dialog.open_for_editor(self._current_editor())

    def _undo(self) -> None:
        editor = self._current_editor()
        if editor is not None:
            editor.undo()

    def _redo(self) -> None:
        editor = self._current_editor()
        if editor is not None:
            editor.redo()

    def _cut(self) -> None:
        editor = self._current_editor()
        if editor is not None:
            editor.cut()

    def _copy(self) -> None:
        editor = self._current_editor()
        if editor is not None:
            editor.copy()

    def _paste(self) -> None:
        editor = self._current_editor()
        if editor is not None:
            editor.paste()

    def _indent_selection(self) -> None:
        editor = self._current_editor()
        if editor is not None:
            editor.indent_selection()

    def _dedent_selection(self) -> None:
        editor = self._current_editor()
        if editor is not None:
            editor.dedent_selection()

    def _comment_selection(self) -> None:
        editor = self._current_editor()
        if editor is not None:
            editor.comment_selection()

    def _show_preferences(self) -> None:
        dialog = SettingsDialog(self.settings_manager, self.theme_manager, self)
        dialog.settings_applied.connect(self._apply_settings_to_open_widgets)
        dialog.exec()

    def _apply_settings_to_open_widgets(self) -> None:
        editor_settings = self.settings_manager.settings.editor
        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)
            if isinstance(widget, CodeEditor):
                widget.apply_settings(editor_settings)
        self.terminal.apply_settings(self.settings_manager.settings.terminal)

    def _show_about(self) -> None:
        about_box = QMessageBox(self)
        about_box.setWindowTitle("About Banter IDE")
        about_box.setTextFormat(Qt.TextFormat.RichText)
        about_box.setText(
            "<h3>Banter IDE — Banter Development Environment</h3>"
            "<p><b>Version 0.1.0</b></p>"
            "<p>A beginner-friendly IDE for learning and teaching Banter.</p>"
            "<p>© 2026 Chuck Finch — Fragillidae Software</p>"
        )
        icon = self.windowIcon()
        if not icon.isNull():
            about_box.setIconPixmap(icon.pixmap(96, 96))
        about_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        about_box.exec()

    def _update_title(self) -> None:
        editor = self._current_editor()
        if editor is None:
            self.setWindowTitle("Banter IDE")
            return
        path_text = editor.file_path.name if editor.file_path else "untitled"
        dirty = "*" if editor.is_dirty() else ""
        self.setWindowTitle(f"Banter IDE - {path_text}{dirty}")

    def _set_theme(self, name: str) -> None:
        self.theme_manager.set_theme(name)
        self._update_theme_menu_selection()

    def _update_theme_menu_selection(self) -> None:
        current = self.theme_manager.current_theme_name()
        for theme_name, action in self.theme_actions.items():
            action.setChecked(theme_name == current)

    def _apply_theme(self, theme_name: str) -> None:
        self._apply_theme_to_widget(self)
        self._apply_theme_to_widget(self.centralWidget())
        self._apply_theme_to_widget(self.file_browser)
        self._apply_theme_to_widget(self.terminal)
        self._apply_theme_to_widget(self.doc_panel)
        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)
            if isinstance(widget, CodeEditor):
                self._apply_theme_to_widget(widget)
        self._update_theme_menu_selection()

    def _apply_theme_to_widget(self, widget) -> None:
        self.theme_manager.apply_to_widget(widget)

    def _set_console_position(self, position: str) -> None:
        if position == "right":
            self.content_splitter.setOrientation(Qt.Orientation.Horizontal)
        else:
            self.content_splitter.setOrientation(Qt.Orientation.Vertical)
        if self.content_splitter.count() >= 2:
            self.content_splitter.setStretchFactor(0, 1)
            self.content_splitter.setStretchFactor(1, 0)

    def _run_code(self) -> None:
        editor = self._current_editor()
        if editor is None:
            return
        self.terminal.write(f"\n> Run ({self.language_provider.name})")
        self.language_provider.run(editor.toPlainText(), self.terminal)
        self.status.showMessage(f"Ran with {self.language_provider.name} provider")

    def _on_terminal_command(self, text: str) -> None:
        self.language_provider.handle_input(text, self.terminal)

    def _restore_window_state(self) -> None:
        geometry = self._settings.value("window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        splitter_state = self._settings.value("window/splitter")
        if splitter_state is not None:
            self.splitter.restoreState(splitter_state)
        content_splitter_state = self._settings.value("window/content_splitter")
        if content_splitter_state is not None:
            self.content_splitter.restoreState(content_splitter_state)

    def _save_window_state(self) -> None:
        self._settings.setValue("window/geometry", self.saveGeometry())
        self._settings.setValue("window/splitter", self.splitter.saveState())
        self._settings.setValue("window/content_splitter", self.content_splitter.saveState())

    def closeEvent(self, event) -> None:
        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)
            if isinstance(widget, CodeEditor) and widget.is_dirty():
                self.tabs.setCurrentIndex(index)
                name = widget.file_path.name if widget.file_path else "untitled"
                reply = QMessageBox.question(
                    self,
                    "Unsaved changes",
                    f"'{name}' has unsaved changes. Close anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    event.ignore()
                    return
        self._save_window_state()
        event.accept()
