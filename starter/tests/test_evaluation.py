import unittest

from src.evaluation import evaluate_query, summarize


class EvaluationTests(unittest.TestCase):
    def question(self):
        return {"id": "q", "split": "dev", "question": "Question", "expected_answer": "Answer",
                "gold_source_id": "doc", "gold_page": 5, "evidence_quote": "Tiếng Việt is useful.", "filter": None}

    def hit(self, text, page=5, source="doc"):
        return {"document_id": source, "page": page, "text": text, "metadata": {"section": "Energy"}}

    def test_unicode_whitespace_and_rank(self):
        result = evaluate_query(self.question(), [self.hit("unrelated", 8), self.hit("Tie\u0302\u0301ng\nVie\u0323\u0302t  is useful.")])
        self.assertFalse(result["hit_at_1"])
        self.assertTrue(result["evidence_hit_at_3"])

    def test_source_page_and_full_evidence_required(self):
        for hits in ([self.hit("Tiếng Việt is useful.", 6)], [self.hit("Tiếng Việt is useful.", source="other")],
                     [self.hit("Tiếng Việt"), self.hit("is useful.")], []):
            self.assertFalse(evaluate_query(self.question(), hits)["evidence_hit_at_3"])

    def test_documented_alternative_accepted(self):
        question = self.question()
        question["alternative_gold_evidence"] = [{"source_id": "other", "page": 9, "evidence_quote": "Equivalent recorded evidence."}]
        self.assertTrue(evaluate_query(question, [self.hit("Equivalent recorded evidence.", 9, "other")])["hit_at_1"])

    def test_rank_four_is_not_hit_three(self):
        hits = [self.hit("irrelevant", 8)] * 3 + [self.hit("Tiếng Việt is useful.")]
        self.assertFalse(evaluate_query(self.question(), hits)["evidence_hit_at_3"])

    def test_summary_and_filter_na(self):
        row = {**evaluate_query(self.question(), [self.hit("Tiếng Việt is useful.")]), "strategy": "A"}
        summary = summarize([row])["metrics"][0]
        self.assertEqual(summary["hit_at_1"], {"numerator": 1, "denominator": 1, "value": 1})
        self.assertIsNone(summary["filter_compliance"]["value"])
        with self.assertRaises(ValueError):
            summarize([row, row])

    def test_empty_results_are_not_filter_compliance(self):
        q = self.question()
        q["filter"] = {"section": "Energy"}
        self.assertFalse(evaluate_query(q, [self.hit("irrelevant"), {**self.hit("x"), "metadata": {"section": "Other"}}])["filter_compliance"])
        self.assertFalse(evaluate_query(q, [])["filter_compliance"])
        self.assertTrue(evaluate_query(q, [self.hit("irrelevant")])["filter_compliance"])


if __name__ == "__main__":
    unittest.main()
