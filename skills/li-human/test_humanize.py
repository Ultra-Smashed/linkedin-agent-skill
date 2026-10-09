import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import detect
import humanize


CLEAN = """Ich habe die Freigabe gestrichen.

6 Tage lag ein Text bei uns. Am Dienstag haben wir das auf 1 Vormittag gekürzt, von rund 18 Stunden auf 4.

Der Trick war klein. Eine Person entscheidet, der Rest liest mit.

Bei euch dauert so eine Runde auch ewig? Bei uns ging es danach mal an einem Vormittag."""


SLOPPY = (
    "In der heutigen schnelllebigen Welt ist es wichtig zu betonen, dass eine "
    "ganzheitliche und nahtlose Transformation essenziell ist.\u200b Darüber hinaus "
    "ermöglicht sie einen bahnbrechenden Mehrwert — „für alle“.\n"
    "Nicht nur schneller, sondern auch günstiger.\n"
    "Das Ergebnis?\n"
    "Was denkst du?"
)


class HumanizeTests(unittest.TestCase):
    def test_invisible_and_inflection(self):
        result = humanize.humanize("Eine naht\u200blose Einführung.")
        self.assertEqual(result.text, "Eine direkte Einführung.")
        self.assertEqual(result.invisible, 1)

    def test_soft_hyphen_rejoins_word(self):
        result = humanize.humanize("ganz\u00adheitlich")
        self.assertEqual(result.text, "komplett")

    def test_nonbreaking_hyphen_still_matches(self):
        result = humanize.humanize("ganz\u2011heitliche Lösung")
        self.assertEqual(result.text, "komplette Lösung")

    def test_case(self):
        self.assertEqual(humanize.humanize("GANZHEITLICH").text, "KOMPLETT")
        self.assertEqual(humanize.humanize("Ganzheitlich").text, "Komplett")

    def test_em_dash_does_not_double_the_period(self):
        self.assertEqual(humanize.humanize("Satz. — Weiter").text, "Satz. Weiter")
        self.assertEqual(humanize.humanize("Warte — wirklich").text, "Warte, wirklich")

    def test_ellipsis(self):
        self.assertEqual(humanize.humanize("Warte…").text, "Warte...")
        self.assertEqual(humanize.humanize("Warte...").text, "Warte...")
        self.assertEqual(humanize.humanize("Warte..").text, "Warte.")
        self.assertEqual(humanize.humanize("Ende.…").text, "Ende...")

    def test_german_quotes_and_en_dash(self):
        self.assertEqual(humanize.humanize("„Hallo“").text, '"Hallo"')
        self.assertEqual(humanize.humanize("2020–2024").text, "2020-2024")

    def test_url_stays(self):
        raw = "Siehe https://example.com/ganzheitlich und bleib ganzheitlich."
        result = humanize.humanize(raw)
        self.assertEqual(
            result.text,
            "Siehe https://example.com/ganzheitlich und bleib komplett.",
        )

    def test_placeholder_stays(self):
        result = humanize.humanize("Es dauerte {{deine Zahl}} und war ganzheitlich.")
        self.assertIn("{{deine Zahl}}", result.text)
        self.assertIn("komplett", result.text)

    def test_structure_is_flagged_not_rewritten(self):
        raw = "Nicht nur schneller, sondern auch günstiger."
        result = humanize.humanize(raw)
        self.assertEqual(result.text, raw)
        self.assertEqual(result.structures[0]["id"], "nicht-nur")

    def test_deleted_opener_keeps_a_capital(self):
        raw = "Es lässt sich nicht leugnen, dass wir wachsen."
        self.assertEqual(humanize.humanize(raw).text, "Wir wachsen.")

    def test_umlaut_word_boundary(self):
        result = humanize.humanize("Die Lösung ist größer und nahtlos.")
        self.assertIn("größer", result.text)
        self.assertIn("direkt", result.text)


class DetectTests(unittest.TestCase):
    def test_clean_passes_and_sloppy_is_flagged(self):
        clean = detect.run(CLEAN)
        sloppy = detect.run(SLOPPY)
        self.assertEqual(clean["label"], "PASS")
        self.assertEqual(sloppy["label"], "FLAGGED")
        self.assertGreater(clean["overall"], sloppy["overall"])

    def test_humanize_lifts_slop_and_fingerprint(self):
        before = detect.run(SLOPPY)
        after_text = humanize.humanize(SLOPPY).text
        after = detect.run(after_text)
        self.assertGreater(after["scores"]["SLOP DENSITY"], before["scores"]["SLOP DENSITY"])
        self.assertGreater(after["scores"]["FINGERPRINT"], before["scores"]["FINGERPRINT"])
        self.assertGreater(after["overall"], before["overall"])
        self.assertTrue(any(hit["id"] == "nicht-nur" for hit in humanize.structure_hits(after_text)))

    def test_voice_penalizes_mixed_address(self):
        mixed = detect.run("Ich zeige dir das. Sie können es morgen nutzen, mal ehrlich, in 3 Tagen.")
        consistent = detect.run("Ich zeige dir das mal in 3 Tagen, und du entscheidest danach.")
        self.assertLess(mixed["scores"]["VOICE"], consistent["scores"]["VOICE"])


if __name__ == "__main__":
    unittest.main()
