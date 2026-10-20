"""Export an offline, single-file demo and a complete review archive."""
from pathlib import Path
import base64
import zipfile
import re
import mimetypes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables'
OUT.mkdir(exist_ok=True)

def data_url(path, mime):
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()

css = (ROOT / 'styles.css').read_text()
for name in ['dm-sans.woff2', 'dm-sans-medium.woff2']:
    css = css.replace('assets/' + name, data_url(ROOT / 'assets' / name, 'font/woff2'))
js = (ROOT / 'app.js').read_text()
js = re.sub(r"ORIGINAL\+'([^']+)'", lambda m: repr('assets/original/' + m.group(1)), js)
html = (ROOT / 'index.html').read_text()
html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>\n' + css + '\n</style>')
html = html.replace('<script src="app.js" defer></script>', '')
html = html.replace('</body>', '<script>\n' + js + '\n</script>\n</body>')
for name in sorted(set(re.findall(r'assets/[\w./-]+\.(?:jpg|png|woff2)',html)),key=len,reverse=True):
    html = html.replace(name,data_url(ROOT/name,mimetypes.guess_type(name)[0] or 'application/octet-stream'))
(OUT / 'Arkaya-Interactive-Demo.html').write_text(html)

with zipfile.ZipFile(OUT / 'Arkaya-Website-Review.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for filename in ['index.html', 'review.html', 'styles.css', 'app.js', 'README.md', 'REVIEW-NOTES.md']:
        path = ROOT / filename
        if path.exists():
            archive.write(path, 'arkaya-demo/' + filename)
    for directory in ['assets', 'tools', 'previews']:
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                if path.name in ['courtyard.png','interior.png']:
                    continue
                archive.write(path, 'arkaya-demo/' + path.relative_to(ROOT).as_posix())
    for path in sorted(OUT.iterdir()):
        if path.suffix.lower() in ['.jpg', '.html', '.json']:
            archive.write(path, 'arkaya-demo/deliverables/' + path.name)
print('Saved standalone HTML and complete review ZIP.')
