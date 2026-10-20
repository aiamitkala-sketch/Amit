"""Export actual browser-rendered JPEGs for every page and homepage section."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import html
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'previews'
OUT.mkdir(exist_ok=True)
BASE='http://127.0.0.1:3000/'
manifest=[]
pages=[('01-homepage','Homepage','/'),('02-projects','Projects listing','/projects'),('03-villa-project','The Neoclassical Villa','/project/neoclassical-villa'),('04-residence-project','Modern Luxe Residence','/project/modern-luxe-residence'),('05-lounge-project','Blue Reverie Lounge','/project/blue-reverie-lounge'),('06-services','Services','/services'),('07-studio','Studio & Founders','/about'),('08-contact','Contact','/contact'),('09-careers','Careers','/careers'),('10-privacy','Demo privacy','/privacy')]
sections=[('01-navigation','Navigation','.site-header'),('02-opening','Opening image & introduction','.hero'),('03-founders','Meet the founders','.founders-section'),('04-selected-projects','Selected projects','.projects-section'),('05-services','Architecture & Interior Design','.services-section'),('06-process','Our process','.process-section'),('07-reels','9:16 Reel previews','.reels-section'),('08-contact','Contact invitation','.contact-band'),('09-footer','Footer & privacy','.site-footer')]

def ready(page):
    page.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")')
    page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
    page.evaluate('document.fonts.ready')

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(device_scale_factor=1)
    for mode,width,height in [('desktop',1440,1000),('mobile',390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        for slug,title,route in pages:
            page.goto(BASE+'#'+route,wait_until='networkidle')
            ready(page)
            name=f'page-{slug}-{mode}.jpg'
            page.screenshot(path=str(OUT/name),full_page=True,type='jpeg',quality=91)
            manifest.append({'kind':'page','title':title,'view':mode,'file':name})
        page.goto(BASE,wait_until='networkidle')
        ready(page)
        # Omit the floating badge from section crops, retaining the page's true layout.
        page.add_style_tag(content='.preview-badge{visibility:hidden!important}')
        for slug,title,selector in sections:
            name=f'section-{slug}-{mode}.jpg'
            page.locator(selector).screenshot(path=str(OUT/name),type='jpeg',quality=94)
            manifest.append({'kind':'section','title':title,'view':mode,'file':name})
    browser.close()

(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
groups=[]
for kind,heading in [('section','Every homepage section'),('page','Every page')]:
    cards=[]
    for item in [m for m in manifest if m['kind']==kind and m['view']=='desktop']:
        mobile=item['file'].replace('-desktop.jpg','-mobile.jpg')
        cards.append(f'<article><h3>{html.escape(item["title"])}</h3><div class="views"><a href="previews/{item["file"]}" target="_blank"><img src="previews/{item["file"]}" alt="Desktop {html.escape(item["title"])}" loading="lazy"><span>Open desktop JPEG ↗</span></a><a href="previews/{mobile}" target="_blank"><img src="previews/{mobile}" alt="Mobile {html.escape(item["title"])}" loading="lazy"><span>Open mobile JPEG ↗</span></a></div></article>')
    groups.append('<section><h2>'+heading+'</h2>'+''.join(cards)+'</section>')
review='''<!doctype html><html lang="en"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Arkkaya — Client review gallery</title><style>*{box-sizing:border-box}body{margin:0;background:#f6f4ef;color:#40352a;font:16px/1.6 Arial,sans-serif;padding:35px 5vw}header{max-width:1000px;margin:0 auto 45px}h1{font-size:44px;font-weight:400;line-height:1.15;letter-spacing:-2px}p{max-width:780px;color:#75675b}nav{display:flex;gap:15px;flex-wrap:wrap}nav a{padding:12px 20px;background:#70513c;color:white;text-decoration:none}section{max-width:1280px;margin:50px auto}h2{font-size:28px;font-weight:400}article{padding:25px 0 40px;border-top:1px solid #d2c5b6}h3{font-size:21px;font-weight:400}.views{display:grid;grid-template-columns:3fr 1fr;gap:25px;align-items:start}a{color:inherit;text-decoration:none}img{width:100%;display:block;box-shadow:0 3px 20px #392c1914}span{display:block;font-size:12px;margin-top:12px}@media(max-width:600px){body{padding:20px}h1{font-size:35px}.views{grid-template-columns:1fr}.views>a:last-child{max-width:240px}nav a{font-size:12px}}</style><header><p>ARKKAYA DESIGN GROUP / SEPARATE CLIENT DEMO</p><h1>The complete redesign,<br>section by section.</h1><p>Actual JPEG captures of the redesigned website, using the original studio logo, founder photo and project images. Every homepage section and all ten pages are shown in desktop and mobile views. Forms are simulated. The original live website is unchanged.</p><nav><a href="index.html">Open interactive demo ↗</a><a href="deliverables/Arkkaya-All-JPEG-Previews.zip">Download all JPEGs ↓</a><a href="deliverables/Arkaya-Website-Review.zip">Download full demo package ↓</a></nav></header>'''+''.join(groups)+'</html>'
(ROOT/'review.html').write_text(review)
with zipfile.ZipFile(ROOT/'deliverables/Arkkaya-All-JPEG-Previews.zip','w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted(OUT.iterdir()):
        z.write(path,'Arkkaya-JPEG-Previews/'+path.name)
print(f'Exported {len(manifest)} JPEGs: 18 section views and 20 full-page views.')
