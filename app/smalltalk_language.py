"""Smalltalk LanguageProvider: syntax highlighting and script execution for Banter IDE.

No Smalltalk interpreter is packaged for this system (gst isn't available
via apt on this Ubuntu release, and squeak-vm is a decade-old GUI VM built
around image files, a poor fit for headless script execution). The run
command is exposed as an editable "Command:" toolbar field rather than a
hardcoded invocation — default text "gst {file}" (GNU Smalltalk's documented
non-interactive script invocation). Kept editable in case you end up on
Pharo instead, which is invoked differently and has no sudo-free apt path
here either.
"""

from __future__ import annotations

import re
import shlex
import tempfile
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QProcess, QSettings
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget

from app.language import LanguageProvider
from app.syntax import BlockCommentHighlighter, HighlightRule, keyword_rule
from app.themes import SyntaxColors

DEFAULT_COMMAND_TEMPLATE = "gst {file}"

SMALLTALK_KEYWORDS = ["true", "false", "nil", "self", "super", "thisContext"]


def _smalltalk_rules() -> List[HighlightRule]:
    return [
        keyword_rule(SMALLTALK_KEYWORDS, "keyword"),
        # Keyword-message selectors, e.g. `at:put:` fragments like `at:`.
        HighlightRule(re.compile(r"\b[a-zA-Z][a-zA-Z0-9]*:"), "builtin"),
        HighlightRule(re.compile(r"#[a-zA-Z][a-zA-Z0-9]*"), "literal"),
        HighlightRule(re.compile(r"\$."), "literal"),
        HighlightRule(re.compile(r"\b\d+\.?\d*\b"), "number"),
        HighlightRule(re.compile(r"'(?:''|[^'])*'"), "string"),
    ]


class SmalltalkHighlighter(BlockCommentHighlighter):
    """Smalltalk comments are `"..."` (double-quotes), the reverse of most
    languages (which use double-quotes for strings). Reuses the shared
    block-comment tracker with identical start/end delimiters."""

    def __init__(self, document: QTextDocument, syntax_colors: SyntaxColors):
        super().__init__(document, syntax_colors, _smalltalk_rules(), r'"', r'"')


class SmalltalkLanguageProvider(LanguageProvider):
    """Runs Smalltalk scripts with a user-editable interpreter command."""

    def __init__(self):
        self._settings = QSettings("BanterIDE", "Banter IDE")
        self._command_template = self._settings.value("smalltalk/command", DEFAULT_COMMAND_TEMPLATE)
        self._process: Optional[QProcess] = None
        self._temp_path: Optional[Path] = None

    @property
    def name(self) -> str:
        return "Smalltalk"

    @property
    def file_extensions(self) -> List[str]:
        return [".st"]

    def create_highlighter(self, document: QTextDocument, syntax_colors: SyntaxColors) -> SmalltalkHighlighter:
        return SmalltalkHighlighter(document, syntax_colors)

    def create_toolbar_widget(self, parent: QWidget) -> QWidget:
        container = QWidget(parent)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(QLabel("Command:"))

        field = QLineEdit(container)
        field.setText(self._command_template)
        field.setMinimumWidth(220)
        field.setToolTip("Run command template. {file} is replaced with the script's temp path.")
        field.editingFinished.connect(lambda: self._set_command(field.text()))
        layout.addWidget(field)
        return container

    def _set_command(self, text: str) -> None:
        text = text.strip() or DEFAULT_COMMAND_TEMPLATE
        self._command_template = text
        self._settings.setValue("smalltalk/command", text)

    def run(self, source: str, terminal) -> None:
        self._stop_process()

        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".st", delete=False, encoding="utf-8")
        tmp.write(source)
        tmp.close()
        self._temp_path = Path(tmp.name)

        try:
            tokens = shlex.split(self._command_template)
        except ValueError as exc:
            terminal.write(f"[error] Invalid command template: {exc}")
            return
        if not tokens:
            terminal.write("[error] Command field is empty")
            return

        args = [str(self._temp_path) if tok == "{file}" else tok for tok in tokens[1:]]

        process = QProcess()
        process.setProgram(tokens[0])
        process.setArguments(args)
        process.readyReadStandardOutput.connect(lambda: self._forward_output(process, terminal))
        process.readyReadStandardError.connect(lambda: self._forward_error(process, terminal))
        process.finished.connect(lambda code, _status: self._on_finished(code, terminal))
        process.errorOccurred.connect(lambda _err: self._on_process_error(process, terminal))
        self._process = process
        process.start()

    def _on_process_error(self, process: QProcess, terminal) -> None:
        if process.error() == QProcess.ProcessError.FailedToStart:
            terminal.write(
                f"[error] Could not start '{process.program()}' — install a Smalltalk "
                "interpreter and/or fix the Command field above."
            )
        else:
            terminal.write(f"[error] {process.errorString()}")

    def handle_input(self, text: str, terminal) -> None:
        if self._process is not None and self._process.state() == QProcess.ProcessState.Running:
            self._process.write((text + "\n").encode("utf-8"))
        else:
            terminal.write("[No running process to receive input]")

    def _forward_output(self, process: QProcess, terminal) -> None:
        data = bytes(process.readAllStandardOutput().data())
        if data:
            terminal.write(data.decode("utf-8", errors="replace").rstrip("\n"))

    def _forward_error(self, process: QProcess, terminal) -> None:
        data = bytes(process.readAllStandardError().data())
        if data:
            terminal.write(data.decode("utf-8", errors="replace").rstrip("\n"))

    def _on_finished(self, exit_code: int, terminal) -> None:
        terminal.write(f"\n[Process exited with code {exit_code}]")
        self._cleanup_temp_file()
        self._process = None

    def _stop_process(self) -> None:
        if self._process is not None:
            self._process.kill()
            self._process.waitForFinished(1000)
            self._process = None
        self._cleanup_temp_file()

    def _cleanup_temp_file(self) -> None:
        if self._temp_path is not None and self._temp_path.exists():
            self._temp_path.unlink(missing_ok=True)
        self._temp_path = None
