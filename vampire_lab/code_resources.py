"""Supports de code téléchargeables à la fin du TD."""
from pathlib import Path

def available_guides():
    folder = Path(__file__).resolve().parent.parent / "docs" / "codes"
    return [(item.stem.replace("_"," ").split(" ",1)[-1], item.name, item.read_text(encoding="utf-8"))
            for item in sorted(folder.glob("*.md"))]
