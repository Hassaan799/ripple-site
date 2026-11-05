#!/usr/bin/env python3
"""Pre-publish checks for the Ripple website.

Fails on broken local links, root-absolute paths (the site lives under /ripple-site/),
bare "#" links, anything loaded from another server, images without alt text, and
unfilled owner details ([[OWNER-...]]) unless --draft is given.

Usage: python3 scripts/check.py [--draft] [ROOT]
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REMOTE = re.compile(r"^(https?:)?//", re.I)
CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", re.I)
LOADED_LINK_RELS = {"stylesheet", "icon", "apple-touch-icon", "preload", "manifest", "modulepreload"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []      # (kind, value): kind "load" must be local, "link" may be remote
        self.ids = set()
        self.missing_alt = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "img" and not (a.get("alt") or "").strip() and a.get("role") != "presentation":
            self.missing_alt += 1
        if "src" in a and a["src"] is not None:
            self.refs.append(("load", a["src"]))
        if tag == "link" and a.get("href"):
            rels = set((a.get("rel") or "").lower().split())
            self.refs.append(("load" if rels & LOADED_LINK_RELS else "link", a["href"]))
        elif tag == "a" and "href" in a:
            self.refs.append(("link", a["href"] or ""))


def check_local(path: Path, root: Path, base: Path, value: str, ids: set) -> list:
    name = path.relative_to(root)
    if value == "#":
        return [f'{name}: bare href="#" (use a real target or no link)']
    if value.startswith("/"):
        return [f"{name}: root-absolute path {value} breaks under /ripple-site/; use a relative path"]
    target, _, fragment = value.partition("#")
    target = target.split("?")[0]
    if not target:
        return [] if fragment in ids else [f"{name}: link to missing #{fragment}"]
    file = (base / target).resolve()
    if file.is_dir():
        file = file / "index.html"
    return [] if file.exists() else [f"{name}: missing file {value}"]


def problems(root: Path, draft: bool) -> list:
    root = Path(root).resolve()
    found = []
    for path in sorted(root.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        page = Page()
        page.feed(text)
        name = path.relative_to(root)
        if page.missing_alt:
            found.append(f"{name}: {page.missing_alt} <img> without alt text")
        if not draft:
            found += [f"{name}: unfilled {m}" for m in sorted(set(re.findall(r"\[\[OWNER-[A-Z]+\]\]", text)))]
        for kind, value in page.refs:
            value = value.strip()
            if value.startswith(("mailto:", "tel:")):
                continue
            if REMOTE.match(value):
                if kind == "load":
                    found.append(f"{name}: loads {value} from another server")
                continue
            found += check_local(path, root, path.parent, value, page.ids)
    for css in sorted(root.rglob("*.css")):
        for value in CSS_URL.findall(css.read_text(encoding="utf-8")):
            if REMOTE.match(value.strip()):
                found.append(f"{css.relative_to(root)}: loads {value} from another server")
    return found


def main(argv):
    draft = "--draft" in argv
    args = [a for a in argv if a != "--draft"]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    found = problems(root, draft)
    for line in found:
        print(line)
    if found:
        return 1
    print(f"OK: {len(list(Path(root).rglob('*.html')))} pages checked" + (" (draft)" if draft else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
