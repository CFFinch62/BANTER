"""Generic regex-rule syntax highlighter, driven by the active theme's SyntaxColors.

Language providers can subclass RuleBasedHighlighter with a list of HighlightRules
instead of writing highlightBlock() from scratch. Colors come from the active
theme, so highlighting stays correct across theme switches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Pattern

from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextDocument

from app.themes import SyntaxColors


@dataclass(frozen=True)
class HighlightRule:
    pattern: Pattern[str]
    color_attr: str  # attribute name on SyntaxColors, e.g. "keyword"
    bold: bool = False


class RuleBasedHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument, syntax_colors: SyntaxColors, rules: List[HighlightRule]):
        super().__init__(document)
        self._rules = rules
        self._formats: Dict[Pattern[str], QTextCharFormat] = {}
        self.set_colors(syntax_colors)

    def set_colors(self, syntax_colors: SyntaxColors) -> None:
        self._syntax_colors = syntax_colors
        self._formats = {}
        for rule in self._rules:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(getattr(syntax_colors, rule.color_attr)))
            if rule.bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            self._formats[rule.pattern] = fmt
        self.rehighlight()

    def format_for(self, color_attr: str, bold: bool = False) -> QTextCharFormat:
        """Build a QTextCharFormat for a SyntaxColors attribute not tied to a specific rule.

        Used by subclasses (e.g. BlockCommentHighlighter) that need a format for
        custom highlightBlock() logic outside the declared `rules` list.
        """
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(getattr(self._syntax_colors, color_attr)))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        return fmt

    def highlightBlock(self, text: str) -> None:
        for rule in self._rules:
            fmt = self._formats[rule.pattern]
            for match in rule.pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


def keyword_rule(words: List[str], color_attr: str = "keyword") -> HighlightRule:
    """Convenience: build a HighlightRule matching a set of whole-word keywords."""
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(w) for w in words) + r")\b")
    return HighlightRule(pattern=pattern, color_attr=color_attr, bold=True)


class BlockCommentHighlighter(RuleBasedHighlighter):
    """RuleBasedHighlighter with correctly-tracked multi-line block comments.

    A single per-line regex can't see a comment that spans multiple blocks
    (lines), so this tracks comment state across blocks via
    QSyntaxHighlighter's previousBlockState()/setCurrentBlockState(), the same
    technique Qt's own multi-line C++ comment highlighter example uses.
    Works whether the start/end delimiters differ (`/*` `*/`) or are
    identical (Smalltalk's `"..."`), since it always resumes searching from
    the previous match's .end() rather than a fixed offset.
    """

    def __init__(
        self,
        document: QTextDocument,
        syntax_colors: SyntaxColors,
        rules: List[HighlightRule],
        comment_start: str,
        comment_end: str,
    ):
        self._comment_start = re.compile(comment_start)
        self._comment_end = re.compile(comment_end)
        super().__init__(document, syntax_colors, rules)

    def highlightBlock(self, text: str) -> None:
        super().highlightBlock(text)
        comment_format = self.format_for("comment")

        if self.previousBlockState() == 1:
            search_from = 0
            open_end = 0
        else:
            start_match = self._comment_start.search(text)
            if start_match is None:
                self.setCurrentBlockState(0)
                return
            search_from = start_match.start()
            open_end = start_match.end()

        while True:
            end_match = self._comment_end.search(text, open_end)
            if end_match is None:
                self.setCurrentBlockState(1)
                self.setFormat(search_from, len(text) - search_from, comment_format)
                return
            self.setCurrentBlockState(0)
            self.setFormat(search_from, end_match.end() - search_from, comment_format)
            next_start = self._comment_start.search(text, end_match.end())
            if next_start is None:
                return
            search_from = next_start.start()
            open_end = next_start.end()
