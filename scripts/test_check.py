"""Tests for scripts/check.py. Run: python3 -m unittest scripts/test_check.py -v"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check import problems  # noqa: E402

PAGE = """<!doctype html><html lang="en"><head><link rel="stylesheet" href="assets/style.css"></head>
<body><h1 id="top">Hi</h1>{body}</body></html>"""


class CheckTests(unittest.TestCase):
    def site(self, body="", css="body{}", extra=None):
        root = Path(tempfile.mkdtemp())
        (root / "assets").mkdir()
        (root / "assets/style.css").write_text(css)
        (root / "index.html").write_text(PAGE.format(body=body))
        for name, text in (extra or {}).items():
            (root / name).write_text(text)
        return root

    def assertProblem(self, found, *parts):
        self.assertTrue(any(all(p in line for p in parts) for line in found), f"{parts} not in {found}")

    def test_clean_site_passes(self):
        root = self.site('<a href="about.html">About</a><a href="#top">Top</a><img src="assets/style.css" alt="x">',
                         extra={"about.html": PAGE.format(body="")})
        self.assertEqual(problems(root, draft=False), [])

    def test_missing_file_fails(self):
        self.assertProblem(problems(self.site('<a href="nope.html">x</a>'), False), "index.html", "nope.html")

    def test_root_absolute_path_fails(self):
        self.assertProblem(problems(self.site('<a href="/index.html">x</a>'), False), "index.html", "/index.html")

    def test_href_hash_fails(self):
        self.assertProblem(problems(self.site('<a href="#">x</a>'), False), "index.html", '"#"')

    def test_missing_fragment_fails(self):
        self.assertProblem(problems(self.site('<a href="#pricing">x</a>'), False), "index.html", "#pricing")

    def test_external_stylesheet_fails(self):
        body = '<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Inter">'
        self.assertProblem(problems(self.site(body), False), "index.html", "fonts.googleapis.com")

    def test_external_script_fails(self):
        self.assertProblem(problems(self.site('<script src="//cdn.example.com/x.js"></script>'), False),
                           "index.html", "cdn.example.com")

    def test_external_css_url_fails(self):
        found = problems(self.site(css="body{background:url(https://example.com/a.png)}"), False)
        self.assertProblem(found, "style.css", "example.com")

    def test_external_link_allowed(self):
        root = self.site('<a href="https://www.lemonsqueezy.com/privacy">LS</a><a href="mailto:a@b.c">mail</a>')
        self.assertEqual(problems(root, False), [])

    def test_missing_alt_fails(self):
        self.assertProblem(problems(self.site('<img src="assets/style.css">'), False), "index.html", "alt")

    def test_marker_fails_unless_draft(self):
        root = self.site("<p>[[OWNER-EMAIL]]</p>")
        self.assertProblem(problems(root, False), "index.html", "[[OWNER-EMAIL]]")
        self.assertEqual(problems(root, True), [])


if __name__ == "__main__":
    unittest.main()
