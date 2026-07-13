import json
from pathlib import Path
from typing import List

from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QFileSystemModel


class FileBrowserWidget(QWidget):
    """Left-side file explorer with basic navigation, bookmarks, and open requests."""

    request_open = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history: List[str] = []
        self._history_index = -1
        self._bookmarks: List[str] = []
        self.bookmarks_file = Path.home() / ".base_ide" / "bookmarks.json"
        self._setup_ui()
        self._load_bookmarks()
        self.navigate_to(str(Path.home()))

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)
        toolbar.setSpacing(4)

        self.back_btn = QToolButton()
        self.back_btn.setText("←")
        self.back_btn.setToolTip("Back")
        self.back_btn.clicked.connect(self._go_back)
        toolbar.addWidget(self.back_btn)

        self.forward_btn = QToolButton()
        self.forward_btn.setText("→")
        self.forward_btn.setToolTip("Forward")
        self.forward_btn.clicked.connect(self._go_forward)
        toolbar.addWidget(self.forward_btn)

        self.up_btn = QToolButton()
        self.up_btn.setText("↑")
        self.up_btn.setToolTip("Go Up")
        self.up_btn.clicked.connect(self._go_up)
        toolbar.addWidget(self.up_btn)

        self.home_btn = QToolButton()
        self.home_btn.setText("⌂")
        self.home_btn.setToolTip("Go Home")
        self.home_btn.clicked.connect(lambda: self.navigate_to(str(Path.home())))
        toolbar.addWidget(self.home_btn)

        self.refresh_btn = QToolButton()
        self.refresh_btn.setText("⟳")
        self.refresh_btn.setToolTip("Refresh")
        self.refresh_btn.clicked.connect(self._refresh)
        toolbar.addWidget(self.refresh_btn)

        self.bookmark_btn = QToolButton()
        self.bookmark_btn.setText("★")
        self.bookmark_btn.setToolTip("Bookmark current folder")
        self.bookmark_btn.clicked.connect(self._bookmark_current_folder)
        toolbar.addWidget(self.bookmark_btn)

        layout.addLayout(toolbar)

        self.path_bar = QLineEdit()
        self.path_bar.setPlaceholderText("Enter path")
        self.path_bar.returnPressed.connect(self._navigate_from_bar)
        layout.addWidget(self.path_bar)

        self.bookmark_list = QListWidget()
        self.bookmark_list.setMaximumHeight(120)
        self.bookmark_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmark_list.customContextMenuRequested.connect(self._show_bookmark_menu)
        self.bookmark_list.itemActivated.connect(self._bookmark_item_clicked)
        layout.addWidget(self.bookmark_list)

        self.model = QFileSystemModel(self)
        self.model.setRootPath(str(Path.home()))
        self.model.setReadOnly(True)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.clicked.connect(self._on_tree_clicked)
        self.tree_view.doubleClicked.connect(self._on_tree_double_clicked)
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)
        layout.addWidget(self.tree_view)

    def navigate_to(self, path: str, add_to_history: bool = True) -> None:
        path_obj = Path(path).expanduser().resolve()
        if not path_obj.exists():
            return
        if path_obj.is_file():
            path_obj = path_obj.parent
        self.model.setRootPath(str(path_obj))
        self.tree_view.setRootIndex(self.model.index(str(path_obj)))
        self.path_bar.setText(str(path_obj))
        if add_to_history:
            self._push_history(str(path_obj))
        self._update_navigation_state()

    def _push_history(self, path: str) -> None:
        if self._history and self._history[-1] == path:
            return
        if self._history_index < len(self._history) - 1:
            self._history = self._history[: self._history_index + 1]
        self._history.append(path)
        self._history_index = len(self._history) - 1
        self._update_navigation_state()

    def _go_back(self) -> None:
        if self._history_index > 0:
            self._history_index -= 1
            self.navigate_to(self._history[self._history_index], add_to_history=False)

    def _go_forward(self) -> None:
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.navigate_to(self._history[self._history_index], add_to_history=False)

    def _go_up(self) -> None:
        current = Path(self.path_bar.text())
        if current.parent.exists():
            self.navigate_to(str(current.parent))

    def _refresh(self) -> None:
        self.model.refresh()

    def _navigate_from_bar(self) -> None:
        self.navigate_to(self.path_bar.text())

    def _bookmark_current_folder(self) -> None:
        current = self.path_bar.text().strip()
        if current and current not in self._bookmarks:
            self._bookmarks.append(current)
            self._save_bookmarks()
            self._refresh_bookmarks()

    def _refresh_bookmarks(self) -> None:
        self.bookmark_list.clear()
        for bookmark in self._bookmarks:
            self.bookmark_list.addItem(bookmark)

    def _load_bookmarks(self) -> None:
        self.bookmarks_file.parent.mkdir(parents=True, exist_ok=True)
        if self.bookmarks_file.exists():
            try:
                self._bookmarks = json.loads(self.bookmarks_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._bookmarks = []
        self._refresh_bookmarks()

    def _save_bookmarks(self) -> None:
        self.bookmarks_file.parent.mkdir(parents=True, exist_ok=True)
        self.bookmarks_file.write_text(json.dumps(self._bookmarks, indent=2), encoding="utf-8")

    def _bookmark_item_clicked(self, item: QListWidgetItem) -> None:
        self.navigate_to(item.text())

    def _show_bookmark_menu(self, position) -> None:
        item = self.bookmark_list.itemAt(position)
        if item is None:
            return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove bookmark")
        action = menu.exec(self.bookmark_list.mapToGlobal(position))
        if action == remove_action:
            self._bookmarks.remove(item.text())
            self._save_bookmarks()
            self._refresh_bookmarks()

    def _update_navigation_state(self) -> None:
        self.back_btn.setEnabled(self._history_index > 0)
        self.forward_btn.setEnabled(self._history_index < len(self._history) - 1)

    def _on_tree_clicked(self, index: QModelIndex) -> None:
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.path_bar.setText(path)

    def _on_tree_double_clicked(self, index: QModelIndex) -> None:
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.navigate_to(path)
        else:
            self.request_open.emit(path)

    def apply_theme(self, theme) -> None:
        self.setStyleSheet(
            f"QWidget {{ background-color: {theme.panel_background}; color: {theme.foreground}; }}"
            f"QLineEdit, QListWidget, QTreeView {{ background-color: {theme.browser_background}; color: {theme.foreground}; border: 1px solid {theme.panel_border}; }}"
            f"QToolButton {{ background-color: {theme.button_background}; color: {theme.button_foreground}; border: 1px solid {theme.input_border}; }}"
            f"QToolButton:hover {{ background-color: {theme.button_hover}; }}"
            f"QTreeView::item:hover {{ background-color: {theme.browser_item_hover}; }}"
            f"QTreeView::item:selected {{ background-color: {theme.browser_item_selected}; color: {theme.background}; }}"
            f"QListWidget::item:hover {{ background-color: {theme.browser_item_hover}; }}"
            f"QListWidget::item:selected {{ background-color: {theme.browser_item_selected}; color: {theme.background}; }}"
        )
