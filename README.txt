SOLITAIRE - IAN DEVELOPMENT HANDOFF

Run Solitaire.exe on Windows to play.
Source: solitaire.py (Python 3 with Tkinter); build recipe: Solitaire.spec.
To develop: install Python 3, pip install pyinstaller, then run python solitaire.py.
To rebuild: python -m PyInstaller --noconfirm Solitaire.spec from this directory.
Keep card_images next to solitaire.py. The build recipe bundles card_images into the executable.

Current features: drag/drop stacks, double-click moves, Undo, score/moves, Easy/Classic/Hard, Hint, and bat emblem on green felt.
Hint highlights a suggested legal move without playing it. Suggestions are heuristic, not guaranteed winning moves.

Artwork source and attribution are in CARD_ART_SOURCE.txt and CARD_ART_CREDITS.txt.
This package includes the executable, source, card assets, and build configuration.
