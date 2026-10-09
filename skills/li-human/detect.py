#!/usr/bin/env python3
"""Fünf lokale Checks. Höher ist menschlicher. Keine Detector-API."""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

from humanize import fingerprint_bits, load_lexicon, slop_spans, structure_hits

CHECKS = ["BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"]
ABBREVIATIONS = ("z. B.", "d. h.", "u. a.", "bzw.", "ca.", "Dr.", "Nr.", "Abs.", "etc.")
WORD = re.compile(r"[A-Za-zÄÖÜäöüß0-9]+(?:['-][A-Za-zÄÖÜäöüß0-9]+)?")
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
UNIT = re.compile(r"\b(?:Euro|Prozent|Minuten|Stunden|Tage|Wochen|Monate|Jahre|Uhr|Kunden)\b", re.IGNORECASE)
FIRST_PERSON = re.compile(
    r"\b(ich|wir|mein|meine|meiner|meinem|meinen|mir|mich|uns|unser|unsere|unserem|unseren)\b",
    re.IGNORECASE,
)
PARTICLE = re.compile(r"\b(mal|eben|halt|eigentlich|irgendwie)\b", re.IGNORECASE)
DU = re.compile(
    r"\b(du|dich|dir|dein|deine|deiner|deinem|deinen|euch|euer|eure|eurer)\b",
    re.IGNORECASE,
)
SIE = re.compile(r"\b(Sie|Ihnen)\b")


def clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def sentences(text: str) -> list[str]:
    protected = text
    for abbrev in ABBREVIATIONS:
        protected = protected.replace(abbrev, abbrev.replace(".", "\u2024"))
    parts = re.split(r"\n+|(?<=[.!?])\s+", protected)
    found: list[str] = []
    for part in parts:
        cleaned = part.replace("\u2024", ".").strip()
        if cleaned:
            found.append(cleaned)
    return found


def words(text: str) -> list[str]:
    return WORD.findall(text)


def check_burstiness(text: str) -> tuple[float, str]:
    lengths = [len(words(sentence)) for sentence in sentences(text)]
    lengths = [count for count in lengths if count]
    if len(lengths) < 3:
        return 60.0, "zu wenige Sätze"
    mean = statistics.fmean(lengths)
    if mean == 0:
        return 60.0, "leer"
    spread = statistics.pstdev(lengths) / mean
    return clamp(spread * 180), f"Streuung {spread:.2f}"


def check_specificity(text: str) -> tuple[float, str]:
    token_count = max(len(words(text)), 1)
    markers = len(NUMBER.findall(text)) + len(UNIT.findall(text)) + text.count("€") + text.count("%")
    per_100 = markers / token_count * 100
    return clamp(per_100 / 3 * 100), f"{markers} Marker, {per_100:.1f} pro 100 Wörter"


def check_slop(text: str, lexicon: dict) -> tuple[float, str]:
    hits = slop_spans(text, lexicon)
    token_count = max(len(words(text)), 1)
    per_100 = len(hits) / token_count * 100
    return clamp(100 - per_100 * 18), f"{len(hits)} Treffer, {per_100:.1f} pro 100 Wörter"


def check_fingerprint(text: str) -> tuple[float, str]:
    invisible, dashes, quotes = fingerprint_bits(text)
    total = invisible + dashes + quotes
    per_k = total / max(len(text), 1) * 1000
    detail = f"{invisible} unsichtbar, {dashes} Gedankenstrich, {quotes} Anführung"
    return clamp(100 - per_k * 25), detail


def check_voice(text: str, lexicon: dict) -> tuple[float, str]:
    score = 45.0
    if FIRST_PERSON.search(text):
        score += 25
    else:
        score -= 15
    if PARTICLE.search(text):
        score += 15
    has_du = DU.search(text) is not None
    has_sie = SIE.search(text) is not None
    if has_du and has_sie:
        score -= 20
    elif has_du or has_sie:
        score += 10
    hits = structure_hits(text, lexicon)
    score -= min(45, len(hits) * 15)
    return clamp(score), f"{len(hits)} Satzmuster"


def judge(scores: dict[str, float]) -> tuple[float, str]:
    values = [scores[name] for name in CHECKS]
    mean = sum(values) / len(values)
    weakest = min(values)
    overall = 0.6 * mean + 0.4 * weakest
    if overall >= 70 and weakest >= 55:
        label = "PASS"
    elif overall >= 50:
        label = "REVIEW"
    else:
        label = "FLAGGED"
    return overall, label


def run(text: str, lexicon: dict | None = None) -> dict:
    lexicon = lexicon or load_lexicon()
    pairs = {
        "BURSTINESS": check_burstiness(text),
        "SPECIFICITY": check_specificity(text),
        "SLOP DENSITY": check_slop(text, lexicon),
        "FINGERPRINT": check_fingerprint(text),
        "VOICE": check_voice(text, lexicon),
    }
    scores = {name: pair[0] for name, pair in pairs.items()}
    details = {name: pair[1] for name, pair in pairs.items()}
    overall, label = judge(scores)
    return {"scores": scores, "details": details, "overall": overall, "label": label}


def bar(score: float, width: int = 24) -> str:
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(result: dict) -> str:
    lines = []
    for name in CHECKS:
        score = result["scores"][name]
        lines.append(f"{name:<13} {bar(score)} {score:5.1f}  {result['details'][name]}")
    lines.append("-" * 60)
    lines.append(f"{'HUMAN SCORE':<13} {bar(result['overall'])} {result['overall']:5.1f}  {result['label']}")
    return "\n".join(lines)


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(path)
    return file_path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Entwurf gegen fünf lokale Checks halten.")
    parser.add_argument("paths", nargs="+", help="Eine Datei, oder vorher und nachher")
    args = parser.parse_args(argv)
    if len(args.paths) > 2:
        print("Höchstens zwei Dateien.", file=sys.stderr)
        return 2
    try:
        texts = [read_text(path) for path in args.paths]
    except FileNotFoundError as exc:
        print(f"Datei fehlt: {exc}", file=sys.stderr)
        return 2
    results = [run(text) for text in texts]
    if len(results) == 1:
        print(render(results[0]))
        return 0
    print("--- vorher ---")
    print(render(results[0]))
    print("--- nachher ---")
    print(render(results[1]))
    delta = results[1]["overall"] - results[0]["overall"]
    sign = "+" if delta >= 0 else ""
    print(f"DELTA  {sign}{delta:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
