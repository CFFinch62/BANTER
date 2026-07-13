# Banter IDE

![Banter IDE banner](banter_banner.svg)

A lightweight PyQt6 IDE for Smalltalk, built on the Base IDE skeleton.

## Features
- Top menu bar (File, Edit, View, Theme)
- Toolbar, including an editable **Command:** field for the run invocation
- Left file browser with navigation controls and bookmarks
- Tabbed editor area with line numbers, current-line highlight, and Smalltalk syntax
  highlighting (including correctly-tracked multi-line `"..."` comments)
- Find/Replace dialog (Ctrl+F)
- Console/terminal panel running the configured command, with an input line
  wired to the running process's stdin
- Status bar with cursor position
- Generic open/save workflow with error dialogs on failure
- Window size, splitter layout, theme, and the run command persisted across restarts

## Requirements
**GNU Smalltalk (`gst`)**, built from source (no apt package exists for this
Ubuntu release). Verified end-to-end: script execution, multi-line
`Transcript` output, and interactive input via `stdin nextLine` all work
correctly. The default Command is:
```
gst {file}
```

### Building GNU Smalltalk from source
Cloned from [gnu-smalltalk/smalltalk](https://github.com/gnu-smalltalk/smalltalk)
to `/home/chuck/Smalltalk/gnu-smalltalk`. Build dependencies (all ordinary
apt packages): `libsigsegv-dev`, `libffi-dev`, `libgmp-dev`,
`libreadline-dev`, `autoconf`, `automake`, `libtool`, `gettext`, `texinfo`,
`gawk`, `bison`, `flex`. Then:
```bash
autoreconf -fi
./configure --prefix="$HOME/Smalltalk/gnu-smalltalk/install" --enable-gtk=no
make
make install
```
`--enable-gtk=no` is required — the optional GTK bindings package fails to
build on Linux (looks for a Windows-only glib header, `glib/gwin32.h`); the
core `gst` interpreter is unaffected and builds cleanly without it.

The installed `gst` is on `PATH` via `~/.bashrc`
(`/home/chuck/Smalltalk/gnu-smalltalk/install/bin`).

### Cuis and Squeak: tried, don't fit this model
Cuis and Squeak (found at `/home/chuck/Smalltalk/`) were both tested against
this IDE and **do not work** with the simple "spawn process → run script →
capture stdout → process exits" model every other provider in this suite
uses. Both are **image-based** environments meant to be opened live and
coded in interactively, not scripted from a shell:

- Invoking `squeak -headless <image> script.st` (the convention documented
  in the VM's own `--help` text) hung indefinitely with **zero output**,
  even with an explicit `Smalltalk snapshot: false andQuit: true.` appended
  to the script and using both bang-chunk (`!`) and plain statement syntax.
  Neither the stock Squeak 6.0 image nor Cuis 7.6 processed the script
  argument as expected.
- Making Cuis/Squeak work here for real would require patching the image
  with custom startup code (read a script path, evaluate it, redirect
  Transcript output somewhere readable, quit) — a fundamentally different
  integration than "point Command field at a binary," and out of scope
  unless specifically revisited.

If you want to use Cuis or Squeak, run them directly via their own launcher
scripts (`RunCuisOnLinux.sh`, `squeak.sh`) as live environments, separate
from this IDE.

## Run
```bash
cd "/home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/IDES/IDE_Suite 2/BANTER"
./run.sh
```
`run.sh` creates `venv/` and installs requirements automatically (via
`setup.sh`) on first run, then launches the app. Run `./setup.sh` directly
if you just want to (re)provision the environment without launching.

## Build a standalone binary
```bash
source venv/bin/activate
python build.py
```
Produces a self-contained app in `dist/BANTER/` via PyInstaller (see
`build.py` and the generated `BANTER.spec`). This only bundles the IDE
itself — the end user still needs a Smalltalk interpreter installed and the
Command field pointed at it.

## Smalltalk support
`app/smalltalk_language.py`'s `SmalltalkLanguageProvider`:
- `create_highlighter` — `SmalltalkHighlighter` subclasses the shared
  `BlockCommentHighlighter` (see `app/syntax.py`) with **identical**
  start/end delimiters (`"`), since Smalltalk uses double-quotes for
  comments and single-quotes for strings — the reverse of most languages.
  Also highlights `true`/`false`/`nil`/`self`/`super`/`thisContext`,
  keyword-message selectors (`at:`, `put:`, etc.), symbols (`#foo`),
  character literals (`$a`), numbers, and `'...'` strings (with `''` escape).
- `create_toolbar_widget` — the editable "Command:" field described above.
- `run` — `shlex.split()`s the command template, substitutes the literal
  `{file}` token with the temp script path as a single argument, and spawns
  it via `QProcess`. A `FailedToStart` error produces a clear message
  pointing at installing an interpreter and/or fixing the Command field.

## Other extension points
- Expand the file browser with project management features such as new folders, rename, and delete.
- Add a preferences dialog for editor font size, tab width, etc.

## License
MIT — see [LICENSE](LICENSE).
