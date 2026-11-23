"""Regression tests for Nathans journal editorial publishing."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_journal.py"
spec = importlib.util.spec_from_file_location("journal_builder", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class JournalBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def article(self, name="safe-article.md", title="Garment Care", body="## Helpful advice\n\nAvoid harsh cleaners."):
        path = self.root / name
        path.write_text("---\ntitle: " + title + "\ndescription: Helpful care information.\ncategory: Professional Dry Cleaning\n---\n\n" + body, encoding="utf-8")
        return path

    def test_parse_valid_article(self):
        article = builder.parse(self.article())
        self.assertEqual(article["slug"], "safe-article")
        self.assertIn("<h2>Helpful advice</h2>", article["html"])

    def test_reject_invalid_slug(self):
        with self.assertRaises(ValueError):
            builder.parse(self.article(name="Unsafe_Name.md"))

    def test_reject_invalid_category(self):
        path = self.article()
        path.write_text(path.read_text().replace("Professional Dry Cleaning", "Unknown category"))
        with self.assertRaises(ValueError):
            builder.parse(path)

    def test_strip_script_from_body(self):
        article = builder.parse(self.article(body="<script>alert('x')</script>\n\nA safe sentence."))
        self.assertNotIn("<script", article["html"])
        self.assertIn("A safe sentence.", article["html"])

    def test_escape_article_title(self):
        article = builder.parse(self.article(title='"Garment & Care"'))
        html = builder.render(article)
        self.assertIn("Garment &amp; Care", html)
        self.assertIn('rel="canonical"', html)

    def test_all_existing_articles_parse(self):
        articles = sorted((SCRIPT.parents[1] / "content" / "journal").glob("*.md"))
        for path in articles:
            if path.name.lower() != "readme.md":
                with self.subTest(path=path.name):
                    builder.parse(path)

if __name__ == "__main__":
    unittest.main()
