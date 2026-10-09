# LinkedIn-Skills für Claude

Elf Claude-Skills, die einen LinkedIn-Account auf Deutsch vorbereiten.
Von [Christopher Thanisch](https://thanisch.co).
Kostenlos, MIT, kein Konto, kein API-Schlüssel, nichts zu verbinden.

Einer schreibt Posts aus 21 Hook-Formeln. Einer kommentiert fremde Posts.
Einer beantwortet die Kommentare unter den eigenen. Einer bewertet das Profil
von 100 Punkten und schreibt die verlorenen Stellen um. Einer plant die Woche:
was, wann, und mit wem.

Der Humanizer macht den Rest brauchbar. Er entfernt Gedankenstriche,
Floskeln und unsichtbare Zeichen, dann bewertet er den Entwurf mit fünf
lokalen Checks, bevor du ihn siehst.

**Nichts geht raus, bis du ja sagst.** Die Skills schreiben. Du postest.

## Installieren

In Claude Code:

```bash
git clone <dieses-repo> linkedin-agent-skill
cp -r linkedin-agent-skill/skills/li-* ~/.claude/skills/
```

Oder als Plugin:

```
/plugin marketplace add <dieses-repo>
/plugin install linkedin-agent
```

Nur für ein Projekt: dieselben Ordner nach `.claude/skills/` im Repo kopieren.

Danach zehn Minuten in `templates/voice.md`. Kopiere sie nach
`~/.claude/linkedin/voice.md` und fülle sie aus, oder füge drei eigene Posts
ein und sag „Schreib meine voice.md daraus“. Jeder Skill liest diese Datei.
Ohne sie klingt alles nach allen anderen.

## Die elf

| Befehl | Was er tut |
| --- | --- |
| `/li-post` | Eine Idee wird ein Post. Drei Hooks aus 21 Formeln, ein Entwurf, humanisiert, bevor du ihn siehst. |
| `/li-comment` | Kommentare auf fremde Posts. Neun Typen, gewählt nach dem Post. Nie „Starker Post!“. |
| `/li-reply` | Der Thread unter dem eigenen Post. Jeder Kommentar wird sortiert, dann in dieser Reihenfolge beantwortet. |
| `/li-profile` | Profil gegen eine 12-teilige Rubrik, 100 Punkte, Umschreiben dort, wo die Punkte fehlen. |
| `/li-plan` | Die Woche. Was posten, wann, und zehn Leute zum Kommentieren. Schreibt `~/.claude/linkedin/plan.md`. |
| `/li-human` | Der Humanizer. Zwei Skripte, die wirklich laufen. Siehe unten. |
| `/li-carousel` | Dokument-Posts. Folientext, ein Cover, das den Swipe verdient, und das PDF zum Hochladen. |
| `/li-repurpose` | Ein Video, ein Newsletter oder ein Transkript wird eine Woche Posts, die jeder für sich stehen. |
| `/li-dm` | Die Notiz mit 200 Zeichen, die erste Nachricht und die zwei Follow-ups. Zwei. |
| `/li-inbox` | Sortiert den Posteingang und sagt, welches Signal die Sequenz verraten hat. |
| `/li-audit` | Nachschau auf veröffentlichte Posts. Rang nach Engagement-Rate und Reichweiten-Vielfachem. |

## Der Humanizer

`/li-human` liefert zwei Python-Skripte ohne Abhängigkeiten. Sie laufen auf
deinem Rechner, auf deinem Text, und nichts wird hochgeladen.

```bash
python3 humanize.py entwurf.txt --report
python3 detect.py entwurf.txt
python3 detect.py vorher.txt nachher.txt
```

**Was automatisch rausgeht:**

- **Unsichtbare Zeichen.** Nullbreite Leerzeichen und Verbinder, weiche
  Trennstriche, Byte-Order-Marken, Unicode-Tags, geschützte und schmale
  Leerzeichen. Die Tastatur erzeugt die nicht. Sie überleben Copy-and-paste
  und sind in jedem Editor unsichtbar.
- **Typografie.** Gedankenstrich zu Komma, Halbgeviertstrich zu Bindestrich,
  geschweifte und deutsche Anführungszeichen zu geraden, Auslassungspunkte zu
  drei Punkten. Dabei entstehen keine doppelten Punkte.
- **Das Lexikon.** Feste Floskeln mit Ersatz in Alltagssprache. Groß- und
  Kleinschreibung bleibt, URLs bleiben unangetastet. Die Liste liegt in
  `skills/li-human/slop.json` und ist zum Bearbeiten da.

**Was nur markiert wird:** „Nicht nur X, sondern Y“, Dreierketten, einwortige
rhetorische Fragen, Hashtag-Wände, Reflex-Köder, gleich lange Sätze.
Die Form eines Satzes braucht Urteil, deshalb kommt das zurück zum Umschreiben
statt als Regex verunstaltet zu werden.

**Die fünf Checks**, 0 bis 100, höher ist menschlicher:

| Check | Was er misst |
| --- | --- |
| BURSTINESS | Schwankung der Satzlänge. Modelle schreiben gleichmäßig. |
| SPECIFICITY | Zahlen, Namen und konkrete Marker pro 100 Wörter. |
| SLOP DENSITY | Lexikon-Treffer pro 100 Wörter. |
| FINGERPRINT | Unsichtbare Zeichen, Gedankenstriche, krumme Anführungen pro 1.000 Zeichen. |
| VOICE | Anrede, Ich-Form, Modalpartikeln, strukturelle Muster. |

Das Urteil gewichtet den Mittelwert mit 60 Prozent und den **schwächsten
einzelnen Check** mit 40 Prozent, weil ein Detektor nur ein Signal braucht.

Das sind lokale Heuristiken, angelehnt an Signale öffentlicher Detektoren.
Sie laufen nur auf deinem Rechner. Sie sind nicht GPTZero, Originality,
Copyleaks, Winston oder Turnitin, rufen diese Dienste nicht auf und können
deren Urteil nicht versprechen. Wer „nicht erkennbar“ verkauft, verkauft
etwas, das sich nicht halten lässt.

## Das Kleingedruckte

**Diese Skills posten nicht auf LinkedIn, und sie sollen es nicht.** Es gibt
keine offizielle API, um auf ein persönliches Profil zu posten, ohne eine
freigegebene Partner-App. Den Dienst per Browser oder Drittanbieter zu
automatisieren verstößt gegen die
[Nutzungsbedingungen von LinkedIn](https://www.linkedin.com/legal/user-agreement)
und führt zu Einschränkungen. Jeder Skill endet gleich: ein Block zum
Kopieren, und du fügst ihn ein. Das Ja-Gate ist die Konstruktion, keine
nachträgliche Option.

**Nichts hier wird erfunden.** Keine ausgedachten Kennzahlen, Kunden oder
Ergebnisse unter deinem Namen. Fehlt eine Zahl, steht `{{deine Zahl}}` im
Entwurf, jedes Mal.

## Dateien

```
skills/li-post/hooks.json        21 Hook-Formeln
skills/li-human/slop.json        Lexikon, unsichtbare Zeichen, Satzmuster
skills/li-human/humanize.py      die drei Reinigungspässe
skills/li-human/detect.py        die fünf Checks
skills/li-human/test_humanize.py die Tests dazu
skills/li-profile/rubric.json    die 100-Punkte-Rubrik
templates/voice.md               deine Stimme. Zuerst ausfüllen.
```

## Über

[Christopher Thanisch](https://thanisch.co) macht den klaren Einstieg in KI für den Arbeitsalltag: Systeme statt Hypes, mit Tools, Guides und einem Newsletter.

## Lizenz

MIT. Copyright (c) 2026 Christopher Thanisch. [thanisch.co](https://thanisch.co)
