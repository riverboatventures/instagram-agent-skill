"""Run with: python3 -m unittest discover tests"""
import json
import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills")
for d in ("ig-viral", "ig-reel", "ig-caption", "ig-human"):
    sys.path.insert(0, os.path.join(ROOT, d))

import beats  # noqa: E402
import caption  # noqa: E402
import humanize  # noqa: E402
import swipe  # noqa: E402


class Tools(unittest.TestCase):
    def test_counts_as_instagram_shows_them(self):
        self.assertEqual(swipe.to_count("412K"), 412000)
        self.assertEqual(swipe.to_count("1.2M"), 1200000)
        self.assertEqual(swipe.to_count("48.5K followers"), 48500)
        self.assertEqual(swipe.to_count("412,000"), 412000)
        self.assertIsNone(swipe.to_count(""))

    def test_one_baseline_per_batch(self):
        rows = [{"account": "@a", "followers": 50000, "median": 10000, "views": 50000, "hook": "x"},
                {"account": "@b", "followers": 100000, "median": None, "views": 200000, "hook": "y"}]
        a = swipe.analyse(rows, None)
        self.assertEqual([r["outlier"] for r in a["reels"]], [5.0, None])

    def test_sentence_start_is_not_a_name(self):
        self.assertEqual(beats.CONCRETE_RE.findall("It works. Really it does."), [])
        self.assertEqual(len(beats.CONCRETE_RE.findall("We moved to Notion.")), 1)

    def test_comment_below_is_not_a_keyword_ask(self):
        self.assertNotIn("comment a keyword", caption.analyse("Comment below.")["asks"])
        self.assertIn("comment a keyword", caption.analyse("Comment CONTRACT.")["asks"])

    def test_capitals_only_where_a_deletion_exposed_them(self):
        lex = humanize.load_lexicon()
        out, _ = humanize.humanize("Basically, the plan works.\niPhone users, e.g. creators, win.\n", lex)
        self.assertIn("iPhone users, e.g. creators", out)
        self.assertFalse(out[0].islower())

    def test_five_hashtags_is_not_a_wall(self):
        lex = humanize.load_lexicon()
        names = [f["name"] for f in humanize.scan_structures("#a #b #c #d #e", lex)]
        self.assertFalse(any("Hashtag wall" in n for n in names))


if __name__ == "__main__":
    unittest.main()
