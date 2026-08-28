import shutil
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QMenu,
    QMessageBox,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QFileSystemModel

from app.settings import SettingsManager


class FileBrowserWidget(QWidget):
    """Left-side file explorer with basic navigation, bookmarks, and open requests."""

    request_open = pyqtSignal(str)

    def __init__(self, parent=None, settings_manager: Optional[SettingsManager] = None):
        super().__init__(parent)
        self._history: List[str] = []
        self._history_index = -1
        self._settings_manager = settings_manager
        self._setup_ui()
        self._refresh_bookmarks()
        self.navigate_to(str(Path.home()))

    @property
    def _bookmarks(self) -> List[str]:
        if self._settings_manager is None:
            return []
        return self._settings_manager.settings.file_browser.bookmarks

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
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_tree_context_menu)
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
            label = Path(bookmark).name or bookmark
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, bookmark)
            item.setToolTip(bookmark)
            self.bookmark_list.addItem(item)

    def _save_bookmarks(self) -> None:
        if self._settings_manager is not None:
            self._settings_manager.save()

    def _bookmark_item_clicked(self, item: QListWidgetItem) -> None:
        self.navigate_to(item.data(Qt.ItemDataRole.UserRole))

    def _show_bookmark_menu(self, position) -> None:
        item = self.bookmark_list.itemAt(position)
        if item is None:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        remove_action = menu.addAction("Remove bookmark")
        action = menu.exec(self.bookmark_list.mapToGlobal(position))
        if action == remove_action:
            self._bookmarks.remove(path)
            self._save_bookmarks()
            self._refresh_bookmarks()

    # -- New file / folder / rename / delete -------------------------------

    def _show_tree_context_menu(self, position) -> None:
        index = self.tree_view.indexAt(position)
        path = ""
        target_dir = self.path_bar.text().strip() or str(Path.home())

        if index.isValid():
            path = self.model.filePath(index)
            target_dir = path if self.model.isDir(index) else str(Path(path).parent)

        menu = QMenu(self)

        new_file_action = menu.addAction("New File...")
        new_file_action.triggered.connect(lambda: self._create_new_file(target_dir))

        new_folder_action = menu.addAction("New Folder...")
        new_folder_action.triggered.connect(lambda: self._create_new_folder(target_dir))

        if index.isValid():
            menu.addSeparator()

            rename_action = menu.addAction("Rename...")
            rename_action.triggered.connect(lambda: self._rename_item(path))

            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self._delete_item(path))

        menu.addSeparator()
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self._refresh)

        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def _create_new_file(self, directory: str) -> None:
        filename, ok = QInputDialog.getText(self, "New File", "Enter filename:")
        if not ok or not filename:
            return
        new_path = Path(directory) / filename
        if new_path.exists():
            QMessageBox.warning(self, "New File", "A file or folder with that name already exists.")
            return
        try:
            new_path.touch()
        except OSError as exc:
            QMessageBox.critical(self, "New File", f"Could not create file: {exc}")
            return
        self._refresh()
        self.request_open.emit(str(new_path))

    def _create_new_folder(self, directory: str) -> None:
        foldername, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if not ok or not foldername:
            return
        new_path = Path(directory) / foldername
        if new_path.exists():
            QMessageBox.warning(self, "New Folder", "A file or folder with that name already exists.")
            return
        try:
            new_path.mkdir(parents=False)
        except OSError as exc:
            QMessageBox.critical(self, "New Folder", f"Could not create folder: {exc}")
            return
        self._refresh()

    def _rename_item(self, path: str) -> None:
        old_path = Path(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_path.name)
        if not ok or not new_name or new_name == old_path.name:
            return
        new_path = old_path.parent / new_name
        if new_path.exists():
            QMessageBox.warning(self, "Rename", "A file or folder with that name already exists.")
            return
        try:
            old_path.rename(new_path)
        except OSError as exc:
            QMessageBox.critical(self, "Rename", f"Could not rename: {exc}")
            return
        self._refresh()

    def _delete_item(self, path: str) -> None:
        path_obj = Path(path)
        if not path_obj.exists():
            return
        item_type = "folder" if path_obj.is_dir() else "file"
        reply = QMessageBox.question(
            self,
            f"Delete {item_type.capitalize()}",
            f"Are you sure you want to delete this {item_type}?\n{path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if path_obj.is_dir():
                shutil.rmtree(path_obj)
            else:
                path_obj.unlink()
        except OSError as exc:
            QMessageBox.critical(self, "Delete", f"Could not delete {item_type}: {exc}")
            return
        self._refresh()

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
