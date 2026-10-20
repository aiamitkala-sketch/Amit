# Arkkaya — B.Form reference-led revision

A static, responsive redesign guided by the client’s B.Form About-page reference (https://bform.studio/pages/about-us). This revision uses full-width imagery, centred copy, a material-study strip, a simple dot-line process, Montserrat body type and a distinct warmer walnut/oat/clay palette. It retains Arkkaya’s original logo, founder portrait, three project names and project images. The original live website is untouched. Forms and Reel playback are simulated for review.

## Open and review

- `index.html`: interactive website, including all project filters, galleries, service links, enquiry/careers forms and mobile menu.
- `review.html`: a visual gallery with desktop/mobile JPEG links for every homepage section and all ten pages.
- `previews/`: 38 real Chromium JPEG captures (18 section views + 20 complete page views).
- `deliverables/Arkkaya-All-JPEG-Previews.zip`: all 38 JPEGs and an image manifest.
- `deliverables/Arkaya-Interactive-Demo.html`: one self-contained HTML document with bundled images, scripts, styles and fonts.
- `deliverables/Arkaya-Website-Review.zip`: complete source, previews, assets and review notes.

## Local development

No installation, build, database or application credentials are required. From `/workspace/arkaya-demo` start:

```sh
python3 -m http.server 3000 --bind 0.0.0.0 --directory /workspace/arkaya-demo
```

Use local requests only for internal checks; localhost is not a shareable link. Every cloud task is isolated. Use the existing checkout and do not create a Git worktree unless explicitly requested.

## Reproduce previews and validation

The cloud machine has Python, Playwright and Chromium at `/usr/bin/chromium`. With the local demo running:

```sh
python3 tools/package_demo.py
python3 -u tools/validate_demo.py
python3 -u tools/export_all_previews.py
python3 tools/package_demo.py
```

Hash routes need no server rewrites. The single-file HTML has been tested with network disabled after its initial document load; the managed cloud browser blocks direct `file://` navigation, so a direct local-file test was not possible here. No third-party assets are requested by the demo during normal navigation.

## Separate hosting

Publish only to a new demo location. Do not deploy over `https://property-website-theta-ten.vercel.app/`. The source is suitable for static hosting without a build command. Public repository mirrors/CDNs can serve the demo independently of the original Vercel deployment. Vercel deployment is optional and requires its own token; no Vercel token has been supplied.

The JPEGs are actual screenshots, not image-generated mockups. Original images are copied without pixel editing. Montserrat, Cormorant Garamond and the retained DM Sans files are bundled under their SIL OFL licences in assets/. See `REVIEW-NOTES.md` for the implementation status and remaining production requirements.
