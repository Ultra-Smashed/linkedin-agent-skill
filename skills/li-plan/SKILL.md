---
name: li-plan
description: >-
  Plant die LinkedIn-Woche auf Deutsch: was posten, wann, und mit wem
  sprechen. Nutzen bei „plan meine Woche“, „worüber soll ich posten“,
  „Content-Kalender“, „ich habe nichts zu posten“, oder wenn jemand einen
  Zeitplan und eine Liste zum Kommentieren will.
---

# li-plan

Der Raum, in dem entschieden wird. Die anderen Skills führen aus. Einmal pro Woche, am selben Tag.

## Eingabe

Lies `~/.claude/linkedin/voice.md` und `log.md`, wenn sie da sind. Der Plan wiederholt kein Thema der letzten zwei Wochen. Fehlen sie, frag nach vier Dingen und schreib sie auf:

1. Was die Person verkauft, und an wen.
2. Drei oder vier Themen, für die sie bekannt sein will.
3. Was diese Woche wirklich passiert ist: ein Gespräch, eine Zahl, ein Fehler, etwas Gebautes, ein Streit. Daraus kommen Posts.
4. Zehn bis zwanzig Leute oder Firmen, bei denen Sichtbarkeit etwas wert ist.

Anrede und Zeitzone gehören in `voice.md`. Standard für die Zeitzone: Europe/Berlin.

## Was gepostet wird

Vier Posts in der Woche schlagen sieben. Der fünfte ist fast immer der schwache, der den Schnitt zieht.

Mischen, nie zwei vom selben Typ hintereinander:

| Typ | Anteil | Aufgabe |
| --- | --- | --- |
| Beweis | 1 pro Woche | etwas, das passiert ist, mit einer Zahl |
| Meinung | 1 pro Woche | eine Position, die Follower kosten kann |
| Lehre | 1 pro Woche | eine Sache, die der Leser heute tun kann |
| Geschichte | 1 alle zwei Wochen | eine Szene mit einem Satz und einem Preis |
| Angebot | 1 alle zwei Wochen | was du verkaufst, klar gesagt |

Pro Slot: Thema, der konkrete Winkel aus dieser Woche, und die Nummer der Hook-Formel aus `~/.claude/skills/li-post/hooks.json` (im Projekt: `.claude/skills/li-post/hooks.json`). Ein Winkel, kein Oberthema. „KI“ ist kein Plan. „Die Freigabe, die sechs Tage brauchte, weil vier Leute denselben Satz ändern wollten“ ist ein Post.

## Wann

Posten, wenn die Zielgruppe am Schreibtisch sitzt. Für ein B2B-Publikum in einer Zeitzone ist Dienstag bis Donnerstag, 7:30 bis 9:30 Uhr dort, der Arbeitswert. Montagnachmittag und Freitagmorgen sind die zweite Reihe. Wochenende ist für eine persönliche Geschichte oder für nichts.

Den Tag und die Stunde an die Zeitzone der Zielgruppe hängen, wenn sie von der eigenen abweicht.

Sag dazu, wenn es stimmt: Die erste Zeile trägt mehr als die Uhrzeit. Wer Uhrzeiten schleift, bevor die Hooks tragen, schleift das falsche Stück.

## Mit wem

Eine Liste von zehn, in drei Gruppen:

- **5 Reichweite.** Leute mit einem Publikum, zu deren Posts die Person wirklich etwas sagen kann. Kommentieren, bevor 20 Kommentare da sind.
- **3 Gleiche.** Dieselbe Höhe, dasselbe Feld. Die Gruppe, die antwortet.
- **2 Käufer.** Leute, die wirklich kaufen könnten. Wochenlang deren Posts kommentieren, bevor eine DM kommt. Im Kommentar nichts verkaufen.

20 Minuten am Tag, vor dem eigenen Post. Kommentare unter fremden Posts sind das, was den eigenen Post tragen hilft.

## Ausgabe

```
WOCHE VOM 8. SEP

MO   nur kommentieren  (20 Min., Liste unten)
DI   8:15  BEWEIS    #17 Zeitanker     die Freigabe von 6 Tagen auf einen Vormittag
MI   nur kommentieren
DO   8:00  MEINUNG   #1  Gegenposition  warum wir das Kick-off gestrichen haben
FR   8:30  LEHRE     #21 Direkter Nutzen  die 4 Zeilen für eine verspätete Lieferung
SA   –
SO   16:00 GESCHICHTE #9 Szenenstart    der Anruf, in dem die Rechnung vor dem Ergebnis lag

KOMMENTIEREN  (5 Reichweite / 3 Gleiche / 2 Käufer)
  ...

Sag „schreib Dienstag“, dann entwerfe ich den Post über /li-post.
```

Den Plan nach `~/.claude/linkedin/plan.md` schreiben, damit die anderen Skills ihn lesen. Nichts wird eingeplant oder veröffentlicht. Die Person führt den Plan aus.

## Grenzen

Erfinde keine Zahlen und keine Gespräche, die diese Woche nicht stattgefunden haben. Fehlt der Beleg, setze `{{deine Zahl}}` und frag danach.

Dieser Skill postet nichts und verschickt nichts.
