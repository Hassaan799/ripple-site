# Ripple website

Static site for Ripple, published with GitHub Pages at
https://hassaan799.github.io/ripple-site/. Plain HTML, one stylesheet
(`assets/style.css`) and one small script (`assets/blob.js`). Nothing to install or build.

## Before every publish

```sh
python3 scripts/check.py
```

It must print `OK`. It fails on broken links, root-absolute paths (the site lives
under `/ripple-site/`, so links must be relative), anything loaded from another
server (no web fonts, analytics or CDNs — this keeps the site cookie-free), images
without alt text, and unfilled owner details (`[[OWNER-…]]`). Use `--draft` while
details are still missing. `python3 -m unittest scripts/test_check.py` tests the checker.

Publish by committing and pushing `main`; GitHub Pages updates within a few minutes.

## Switching on Buy and Download

Until checkout and a notarized download exist, these are disabled
`<a class="button is-soon" aria-disabled="true">` elements in `index.html`
(hero download button and both pricing cards). To switch one on: add
`href="<URL>"`, remove `is-soon` and `aria-disabled`, and change the text
("Download for Mac", "Start monthly", "Start yearly").

## Owner details

Name, address and email appear in `impressum.html`, `contact.html`,
`privacy.html` and the footer `mailto:` links. Search for the email to change it everywhere.

## Images

`scripts/make_images.py` rebuilds `assets/img/` from the app repo's
`Branding/screenshots/` (resizes, blurs the album cover, makes icons and the
share image). Never use the lock-screen preview screenshot or real album art.
