from __future__ import annotations

import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from arxiv_aggregate import dedup_states  # noqa: E402
from scraper.arxiv_extract import (  # noqa: E402
    _extract_theorem_environments,
    _pdf_excerpt,
)


class ArxivHtmlExtractionTests(unittest.TestCase):
    def test_short_open_problem_aliases_are_extracted(self):
        for env_type in ("qn", "qu", "open", "Conjecture"):
            with self.subTest(env_type=env_type):
                soup = BeautifulSoup(
                    f"""
                    <div class="ltx_theorem ltx_theorem_{env_type}">
                      <h6 class="ltx_title_theorem">
                        <span class="ltx_tag_theorem">Question 1</span>
                      </h6>
                      <div class="ltx_para"><p>Is this true?</p></div>
                    </div>
                    """,
                    "lxml",
                )
                environments = _extract_theorem_environments(soup)
                self.assertEqual(len(environments), 1)
                self.assertTrue(environments[0]["of_interest"])
                self.assertEqual(environments[0]["statement"], "Is this true?")

    def test_statement_includes_sibling_display_equation(self):
        soup = BeautifulSoup(
            r"""
            <div class="ltx_theorem ltx_theorem_conjecture">
              <h6 class="ltx_title_theorem">
                <span class="ltx_tag_theorem">Conjecture 5</span>
              </h6>
              <div class="ltx_para">
                <p>We have</p>
                <table class="ltx_equation"><tr><td>
                  <math display="block"><semantics>
                    <annotation encoding="application/x-tex">m_k(n)\sim n.</annotation>
                  </semantics></math>
                </td></tr></table>
              </div>
            </div>
            """,
            "lxml",
        )
        statement = _extract_theorem_environments(soup)[0]["statement"]
        self.assertEqual(statement, "We have\n\n" + r"$$m_k(n)\sim n.$$")

    def test_pdf_excerpt_keeps_head_and_tail(self):
        text = "HEAD-" + "x" * 20 + "-TAIL"
        excerpt = _pdf_excerpt(text, edge_chars=5)
        self.assertTrue(excerpt.startswith("HEAD-"))
        self.assertTrue(excerpt.endswith("-TAIL"))
        self.assertIn("PDF characters omitted", excerpt)


class ArxivDedupTests(unittest.TestCase):
    @staticmethod
    def record(arxiv_id: str, title: str, statement: str) -> dict:
        return {
            "arxiv_id": arxiv_id,
            "title": title,
            "statement_text": statement,
            "paper_authors": ["Ada Author"],
            "published": "2026-01-01",
            "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
            "paper_title": "Paper",
        }

    def test_placeholder_records_are_never_deduplicated(self):
        records = [
            self.record("2600.00001", "Question 1", "[Full statement not available.]"),
            self.record("2600.00001", "Question 2", "[Full statement not available.]"),
        ]
        self.assertEqual(len(dedup_states(records)), 2)

    def test_same_paper_duplicate_does_not_create_self_reference(self):
        records = [
            self.record("2600.00001", "Conjecture 1", "Every graph is blue."),
            self.record("2600.00001", "Conjecture 2", "Every graph is blue."),
        ]
        deduped = dedup_states(records)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0]["also_stated_in"], [])

    def test_curated_distinct_record_can_bypass_fuzzy_dedup(self):
        first = self.record("2600.00001", "Conjecture 1", "Every graph is blue.")
        second = self.record("2600.00001", "Conjecture 2", "Every graph is blue.")
        second["_dedup_exempt"] = True
        deduped = dedup_states([first, second])
        self.assertEqual(len(deduped), 2)
        self.assertNotIn("_dedup_exempt", deduped[1])


if __name__ == "__main__":
    unittest.main()
