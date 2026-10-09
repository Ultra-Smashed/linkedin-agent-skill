#!/usr/bin/env python3
"""Drei Reinigungspässe für deutsche Entwürfe. Keine Abhängigkeiten."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

LEXICON_PATH = Path(__file__).with_name("slop.json")
TOKEN = re.compile(r"\uE000\d+\uE001")
SPACE_INSTEAD = set("\u00a0\u202f\u2007\u2009\u200a")
HYPHEN_CHARS = "\u2010\u2011\u2012\u2212\ufe63\uff0d"
DOUBLE_QUOTES = "„“”«»‹›‟❝❞"
SINGLE_QUOTES = "‘’‚‛"
DASHES = "\u2014\u2013\u2015"

_CACHE: dict | None = None


def is_invisible(ch: str) -> bool:
    if ch in SPACE_INSTEAD or ch in "\u200b\u200c\u200d\u2060\ufeff\u00ad\u200e\u200f":
        return True
    if ch in "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069":
        return True
    if unicodedata.category(ch) == "Cf":
        return True
    code = ord(ch)
    return 0xE0000 <= code <= 0xE007F


def load_lexicon(path: Path | None = None) -> dict:
    global _CACHE
    source = Path(path) if path else LEXICON_PATH
    if path is None and _CACHE is not None:
        return _CACHE
    data = json.loads(source.read_text(encoding="utf-8"))
    for entry in data["words"]:
        entry["pattern"] = compile_word(entry["find"], bool(entry.get("inflect")))
    for entry in data["phrases"]:
        entry["pattern"] = compile_phrase(entry["find"])
    for entry in data["structures"]:
        entry["pattern"] = re.compile(entry["regex"], re.IGNORECASE | re.MULTILINE)
    if path is None:
        _CACHE = data
    return data


def compile_word(find: str, inflect: bool) -> re.Pattern[str]:
    body = "-?".join(re.escape(ch) for ch in find)
    if inflect:
        pattern = rf"(?<![\w])({body})(e|er|es|en|em)?(?![\w])"
    else:
        pattern = rf"(?<![\w])({body})(?![\w])"
    return re.compile(pattern, re.IGNORECASE)


def compile_phrase(find: str) -> re.Pattern[str]:
    parts = [re.escape(part) for part in find.split()]
    body = r"\s+".join(parts)
    return re.compile(rf"(?<![\w])({body})(?![\w])", re.IGNORECASE)


def protect(text: str) -> tuple[str, list[str]]:
    found: list[str] = []

    def take(match: re.Match[str]) -> str:
        found.append(match.group(0))
        return f"\uE000{len(found) - 1}\uE001"

    guarded = re.sub(r"https?://\S+|www\.\S+", take, text)
    guarded = re.sub(r"\{\{.*?\}\}", take, guarded)
    return guarded, found


def restore(text: str, found: list[str]) -> str:
    def put(match: re.Match[str]) -> str:
        return found[int(match.group(1))]

    return re.sub(r"\uE000(\d+)\uE001", put, text)


def pass_invisible(text: str) -> tuple[str, int]:
    out: list[str] = []
    count = 0
    for ch in text:
        if not is_invisible(ch):
            out.append(ch)
            continue
        count += 1
        if ch in SPACE_INSTEAD:
            out.append(" ")
    return "".join(out), count


def tidy_punct(text: str, *, final: bool = False) -> str:
    sentinel = "\uE010"
    text = text.replace("...", sentinel)
    text = re.sub(r"\.{2,}", ".", text)
    text = text.replace(sentinel, "...")
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s*\.", ".", text)
    text = re.sub(r"\.\s*,", ".", text)
    text = re.sub(r",(?:\s*,)+", ",", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" +([,.;:!?])", r"\1", text)
    text = re.sub(r"(^|\n)\s*[,;:]+\s*", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not final:
        return text
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def pass_typography(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    text = text.replace("\u2026", "...")
    text = re.sub(r"\.{4,}", "...", text)
    if re.search(r"[\u2014\u2015]", text):
        notes.append("Gedankenstrich")
        text = re.sub(r"[ \t]*[\u2014\u2015][ \t]*", ", ", text)
    if "\u2013" in text:
        notes.append("Halbgeviertstrich")
        text = re.sub(r"(?<=\d)\u2013(?=\d)", "-", text)
        text = text.replace("\u2013", "-")
    if any(ch in text for ch in HYPHEN_CHARS):
        notes.append("Bindestrich")
        for ch in HYPHEN_CHARS:
            text = text.replace(ch, "-")
    if any(ch in text for ch in DOUBLE_QUOTES):
        notes.append("Anführungszeichen")
        for ch in DOUBLE_QUOTES:
            text = text.replace(ch, '"')
    if any(ch in text for ch in SINGLE_QUOTES):
        notes.append("Apostroph")
        for ch in SINGLE_QUOTES:
            text = text.replace(ch, "'")
    if "•" in text:
        notes.append("Aufzählungspunkt")
        text = text.replace("•", "-")
    return tidy_punct(text), notes


def recap_leading(original: str, updated: str) -> str:
    original_lead = original.lstrip()[:1]
    updated_lead = updated.lstrip()[:1]
    if original_lead.isupper() and updated_lead.islower():
        stripped = updated.lstrip()
        return stripped[0].upper() + stripped[1:]
    return updated


def apply_case(sample: str, replacement: str) -> str:
    if not sample or not replacement:
        return replacement
    if sample.isupper():
        return replacement.upper()
    if sample[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement[0].lower() + replacement[1:]


def render_replacement(match: re.Match[str], entry: dict) -> str:
    replacement = entry.get("replace") or ""
    if not replacement:
        return ""
    suffix = ""
    if entry.get("inflect"):
        suffix = match.group(2) or ""
    sample = match.group(1).replace("-", "")
    return apply_case(sample, replacement + suffix.lower())


def find_matches(text: str, entries: list[dict]) -> list[tuple[int, int, re.Match[str], dict]]:
    found: list[tuple[int, int, re.Match[str], dict]] = []
    for entry in entries:
        for match in entry["pattern"].finditer(text):
            found.append((match.start(), match.end(), match, entry))
    found.sort(key=lambda item: (-(item[1] - item[0]), item[0]))
    accepted: list[tuple[int, int, re.Match[str], dict]] = []
    for cand in found:
        overlaps = any(not (cand[1] <= prev[0] or cand[0] >= prev[1]) for prev in accepted)
        if overlaps:
            continue
        accepted.append(cand)
    accepted.sort(key=lambda item: item[0])
    return accepted


def replace_entries(text: str, entries: list[dict]) -> tuple[str, list[tuple[str, str]]]:
    chosen = find_matches(text, entries)
    pieces: list[str] = []
    changes: list[tuple[str, str]] = []
    last = 0
    for start, end, match, entry in chosen:
        pieces.append(text[last:start])
        rendered = render_replacement(match, entry)
        changes.append((match.group(0), rendered))
        pieces.append(rendered)
        last = end
    pieces.append(text[last:])
    return "".join(pieces), changes


def fix_caps(text: str) -> str:
    def lift(match: re.Match[str]) -> str:
        return match.group(1) + match.group(2).upper()

    return re.sub(r"((?<![A-ZÄÖÜ])[.!?]\s+|:\s+)([a-zäöü])", lift, text)


def map_outside(text: str, fn) -> str:
    pieces: list[str] = []
    last = 0
    for match in TOKEN.finditer(text):
        pieces.append(fn(text[last : match.start()]))
        pieces.append(match.group(0))
        last = match.end()
    pieces.append(fn(text[last:]))
    return "".join(pieces)


def structure_hits(text: str, lexicon: dict | None = None) -> list[dict]:
    lexicon = lexicon or load_lexicon()
    hits: list[dict] = []
    for entry in lexicon["structures"]:
        for match in entry["pattern"].finditer(text):
            snippet = " ".join(match.group(0).split())
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."
            hits.append({"id": entry["id"], "name": entry["name"], "snippet": snippet})
    return hits


def slop_spans(text: str, lexicon: dict | None = None) -> list[tuple[int, int, str]]:
    lexicon = lexicon or load_lexicon()
    phrases = [(start, end, match.group(0)) for start, end, match, _ in find_matches(text, lexicon["phrases"])]
    words: list[tuple[int, int, str]] = []
    for start, end, match, _entry in find_matches(text, lexicon["words"]):
        if any(not (end <= prev[0] or start >= prev[1]) for prev in phrases):
            continue
        words.append((start, end, match.group(0)))
    return phrases + words


def fingerprint_bits(text: str) -> tuple[int, int, int]:
    invisible = sum(1 for ch in text if is_invisible(ch))
    dashes = sum(text.count(ch) for ch in DASHES)
    quotes = sum(text.count(ch) for ch in DOUBLE_QUOTES + SINGLE_QUOTES)
    return invisible, dashes, quotes


class HumanizeResult:
    def __init__(
        self,
        text: str,
        invisible: int,
        typography: list[str],
        lexicon_changes: list[tuple[str, str]],
        structures: list[dict],
    ):
        self.text = text
        self.invisible = invisible
        self.typography = typography
        self.lexicon_changes = lexicon_changes
        self.structures = structures


def humanize(text: str, lexicon: dict | None = None) -> HumanizeResult:
    lexicon = lexicon or load_lexicon()
    guarded, found = protect(text)
    cleaned, invisible = pass_invisible(guarded)
    typography_notes: list[str] = []

    def apply_typo(chunk: str) -> str:
        updated, notes = pass_typography(chunk)
        typography_notes.extend(notes)
        return updated

    cleaned = map_outside(cleaned, apply_typo)
    phrase_changes: list[tuple[str, str]] = []
    word_changes: list[tuple[str, str]] = []

    def apply_phrases(chunk: str) -> str:
        updated, changes = replace_entries(chunk, lexicon["phrases"])
        phrase_changes.extend(changes)
        return updated

    def apply_words(chunk: str) -> str:
        updated, changes = replace_entries(chunk, lexicon["words"])
        word_changes.extend(changes)
        return updated

    cleaned = map_outside(cleaned, apply_phrases)
    cleaned = map_outside(cleaned, apply_words)
    cleaned = map_outside(cleaned, lambda chunk: fix_caps(tidy_punct(chunk)))
    cleaned = restore(cleaned, found)
    cleaned = recap_leading(text, tidy_punct(cleaned, final=True))
    structures = structure_hits(cleaned, lexicon)
    seen: list[str] = []
    for note in typography_notes:
        if note not in seen:
            seen.append(note)
    return HumanizeResult(cleaned, invisible, seen, phrase_changes + word_changes, structures)


def render_report(result: HumanizeResult) -> str:
    lines = [
        "HUMANIZE",
        f"unsichtbar: {result.invisible} entfernt",
        f"typografie: {', '.join(result.typography) if result.typography else 'keine'}",
        f"lexikon: {len(result.lexicon_changes)} ersetzt",
    ]
    for source, target in result.lexicon_changes:
        lines.append(f"  {source} -> {target or '(entfernt)'}")
    lines.append(f"strukturen: {len(result.structures)} markiert")
    for hit in result.structures:
        lines.append(f"  {hit['id']}: {hit['snippet']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deutschen Entwurf von KI-Spuren reinigen.")
    parser.add_argument("path", help="Textdatei, oder - für stdin")
    parser.add_argument("-o", "--output", help="Bereinigten Text in diese Datei schreiben")
    parser.add_argument("--report", action="store_true", help="Änderungen auf stdout zeigen")
    args = parser.parse_args(argv)
    if args.path == "-":
        raw = sys.stdin.read()
    else:
        file_path = Path(args.path)
        if not file_path.is_file():
            print(f"Datei fehlt: {file_path}", file=sys.stderr)
            return 2
        raw = file_path.read_text(encoding="utf-8")
    result = humanize(raw)
    body = result.text
    if body and not body.endswith("\n"):
        body += "\n"
    if args.output:
        Path(args.output).write_text(body, encoding="utf-8")
    if args.report:
        print(render_report(result))
        if not args.output:
            print()
            print(body, end="" if body.endswith("\n") else "\n")
    elif not args.output:
        print(body, end="" if body.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
