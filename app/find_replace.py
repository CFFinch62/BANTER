from typing import Optional

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from app.editor import CodeEditor


class FindReplaceDialog(QDialog):
    """Non-modal Find/Replace dialog that operates on whichever CodeEditor is set via set_editor()."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find / Replace")
        self.setModal(False)
        self._editor: Optional[CodeEditor] = None

        layout = QGridLayout(self)

        layout.addWidget(QLabel("Find:"), 0, 0)
        self.find_edit = QLineEdit()
        self.find_edit.returnPressed.connect(lambda: self._find(backward=False))
        layout.addWidget(self.find_edit, 0, 1, 1, 3)

        layout.addWidget(QLabel("Replace:"), 1, 0)
        self.replace_edit = QLineEdit()
        layout.addWidget(self.replace_edit, 1, 1, 1, 3)

        self.case_checkbox = QCheckBox("Case sensitive")
        layout.addWidget(self.case_checkbox, 2, 0, 1, 2)

        find_next_btn = QPushButton("Find Next")
        find_next_btn.clicked.connect(lambda: self._find(backward=False))
        layout.addWidget(find_next_btn, 3, 0)

        find_prev_btn = QPushButton("Find Previous")
        find_prev_btn.clicked.connect(lambda: self._find(backward=True))
        layout.addWidget(find_prev_btn, 3, 1)

        replace_btn = QPushButton("Replace")
        replace_btn.clicked.connect(self._replace)
        layout.addWidget(replace_btn, 3, 2)

        replace_all_btn = QPushButton("Replace All")
        replace_all_btn.clicked.connect(self._replace_all)
        layout.addWidget(replace_all_btn, 3, 3)

    def set_editor(self, editor: Optional[CodeEditor]) -> None:
        self._editor = editor

    def open_for_editor(self, editor: Optional[CodeEditor]) -> None:
        self.set_editor(editor)
        self.show()
        self.raise_()
        self.activateWindow()
        self.find_edit.setFocus()
        self.find_edit.selectAll()

    def _find(self, backward: bool) -> None:
        if self._editor is None:
            return
        text = self.find_edit.text()
        found = self._editor.find_text(text, backward=backward, case_sensitive=self.case_checkbox.isChecked())
        self.find_edit.setStyleSheet("" if found else "background-color: #f38ba8;")

    def _replace(self) -> None:
        if self._editor is None:
            return
        self._editor.replace_current(
            self.find_edit.text(), self.replace_edit.text(), case_sensitive=self.case_checkbox.isChecked()
        )

    def _replace_all(self) -> None:
        if self._editor is None:
            return
        count = self._editor.replace_all(
            self.find_edit.text(), self.replace_edit.text(), case_sensitive=self.case_checkbox.isChecked()
        )
        main_window = self.parent()
        if main_window is not None and hasattr(main_window, "status"):
            main_window.status.showMessage(f"Replaced {count} occurrence(s)")
