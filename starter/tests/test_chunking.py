import unittest
from copy import deepcopy

from src.chunking import by_paragraph, fixed_size
from src.models import DocumentPage


class ChunkingTests(unittest.TestCase):
    def page(self, text):
        return DocumentPage("doc", "source.pdf", 7, text, {"section": "Energy", "nested": {"x": 1}})

    def assert_coverage(self, page, chunks, limit, overlap=False):
        positions = set()
        for chunk in chunks:
            start, end = chunk.metadata["start_char"], chunk.metadata["end_char"]
            self.assertEqual(chunk.text, page.text[start:end])
            self.assertTrue(0 < len(chunk.text) <= limit)
            self.assertEqual((chunk.document_id, chunk.source, chunk.page), ("doc", "source.pdf", 7))
            current = set(range(start, end))
            if not overlap:
                self.assertFalse(positions & current)
            positions.update(current)
        self.assertTrue({i for i, c in enumerate(page.text) if not c.isspace()} <= positions)

    def test_fixed_overlap_and_terminal_chunk(self):
        page = self.page("abcdefghijklmno")
        chunks = fixed_size(page, 6, 2)
        self.assertEqual([c.text for c in chunks], ["abcdef", "efghij", "ijklmn", "mno"])
        self.assert_coverage(page, chunks, 6, overlap=True)
        self.assertEqual(len(fixed_size(self.page("abcdef"), 6, 2)), 1)

    def test_paragraph_boundaries_preferred(self):
        page = self.page("First paragraph.\n\nSecond paragraph.")
        chunks = by_paragraph(page, 20)
        self.assertEqual([c.text for c in chunks], ["First paragraph.", "Second paragraph."])
        self.assert_coverage(page, chunks, 20)

    def test_wrapped_prose_uses_sentence_boundary(self):
        page = self.page("First sentence. Next\nwrapped sentence is longer. Final sentence.")
        chunks = by_paragraph(page, 40)
        self.assertEqual(chunks[0].text, "First sentence.")
        self.assert_coverage(page, chunks, 40)

    def test_multiline_heading_stays_with_following_prose(self):
        page = self.page("ENERGY\nSTORAGE\nFirst short sentence. Another sentence follows. More words follow.")
        chunks = by_paragraph(page, 50)
        self.assertIn("First short sentence.", chunks[0].text)
        self.assert_coverage(page, chunks, 50)

    def test_long_tokens_unicode_and_blank_input(self):
        for text in ("đ" * 51, "TITLE\n\nTiếng Việt.\nDòng tiếp theo.\n\nEND", "\n \t "):
            page = self.page(text)
            for make in (lambda p: by_paragraph(p, 12), lambda p: fixed_size(p, 12, 3)):
                self.assert_coverage(page, make(page), 12, overlap=True)
        self.assertEqual(by_paragraph(self.page(" \n "), 10), [])
        self.assertEqual(fixed_size(self.page(""), 10, 0), [])

    def test_ids_and_metadata_are_stable_and_isolated(self):
        page = self.page("Some source text. Another sentence.")
        original = deepcopy(page)
        for make in (lambda: fixed_size(page, 20, 2), lambda: by_paragraph(page, 20)):
            chunks = make()
            self.assertEqual(chunks, make())
            self.assertEqual(len({c.chunk_id for c in chunks}), len(chunks))
            chunks[0].metadata["nested"]["x"] = 99
            self.assertEqual(page, original)
            if len(chunks) > 1:
                self.assertEqual(chunks[1].metadata["nested"]["x"], 1)
        self.assertNotEqual(fixed_size(page, 20, 0)[0].chunk_id, fixed_size(page, 20, 2)[0].chunk_id)

    def test_invalid_parameters_fail_before_processing(self):
        page = self.page("")
        for size in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                by_paragraph(page, size)
            with self.assertRaises(ValueError):
                fixed_size(page, size, 0)
        for overlap in (-1, 5, 6, True, .5):
            with self.assertRaises(ValueError):
                fixed_size(page, 5, overlap)


if __name__ == "__main__":
    unittest.main()
