"""Validate the real hosted demo using the platform's TLS-verified transport.

Chromium in this machine rejects the proxy certificate, while the platform's
system CA bundle is trusted by Python. Route the browser's HTTPS requests
through that verified system transport, fetching the actual remote responses.
This does not mock files or disable certificate/hostname verification.
"""
from urllib.request import Request, urlopen
from pathlib import Path
import ssl
import json
import sys
import os
from playwright.sync_api import sync_playwright, expect

BASE=sys.argv[1]
ROOT=Path(__file__).resolve().parents[1]
observed=[]
errors=[]
trust=ssl.create_default_context()

def verified_fetch(route):
    url=route.request.url
    try:
        request=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'*/*'})
        with urlopen(request,context=trust,timeout=45) as response:
            data=response.read()
            headers={k:v for k,v in response.headers.items() if k.lower() not in ['content-encoding','content-length','transfer-encoding']}
            observed.append({'url':url,'status':response.status,'bytes':len(data)})
            route.fulfill(status=response.status,headers=headers,body=data)
    except Exception as e:
        errors.append({'url':url,'error':str(e)})
        route.abort()

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.route('https://raw.githack.com/**',verified_fetch)
    page.on('pageerror',lambda e: errors.append({'javascript':str(e)}))
    page.goto(BASE+'index.html',wait_until='networkidle',timeout=120000)
    expect(page.locator('h1')).to_have_text('Spaces for the wayyou live.')
    page.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")')
    page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)',timeout=45000)
    page.locator('.hero-actions a').first.click()
    page.get_by_role('button',name='Architecture',exact=True).click()
    expect(page.locator('#filtered-projects .project-card')).to_have_count(1)
    page.get_by_role('button',name='Interiors',exact=True).click()
    expect(page.locator('#filtered-projects .project-card')).to_have_count(2)
    page.locator('.project-card .view-project').first.click()
    expect(page.locator('h1')).to_have_text('Modern Luxe Residence')
    page.locator('.gallery-tile').first.click()
    expect(page.locator('dialog')).to_be_visible()
    page.keyboard.press('Escape')
    page.goto(BASE+'index.html#/about',wait_until='networkidle',timeout=120000)
    expect(page.locator('.studio-vision h2')).to_have_text('Our vision')
    expect(page.locator('.material-grid img')).to_have_count(5)
    expect(page.locator('.founders-detail h2')).to_have_text('Founders')
    page.goto(BASE+'review.html',wait_until='networkidle',timeout=120000)
    expect(page.locator('h1')).to_contain_text('The complete redesign,')
    expect(page.locator('article')).to_have_count(19)
    page.set_viewport_size({'width':390,'height':844})
    page.goto(BASE+'index.html',wait_until='networkidle',timeout=120000)
    page.get_by_role('button',name='Open navigation',exact=True).click()
    page.locator('#mobile-nav').get_by_role('link',name='Contact',exact=True).click()
    expect(page.locator('h1')).to_have_text('Let’s make roomfor your ideas.')
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    browser.close()

assert not errors,errors
report={'base':BASE,'transport':'Actual remote HTTPS responses via Python system trust store; certificate and hostname verification enabled. Chromium direct proxy trust is unavailable.','checks':['Remote homepage and assets load','Architecture and Interiors filters','Project navigation and gallery','Reference-led Studio vision, founder section and five material studies','Remote review gallery contains all 19 desktop/mobile pairs','Mobile navigation and contact page'],'requests':observed,'outcome':'passed'}
Path(os.environ.get('ARKAYA_HOSTED_REPORT',str(ROOT/'deliverables/hosted-validation.json'))).write_text(json.dumps(report,indent=2))
print('Hosted demo checks passed:',len(report['checks']),'functional checks;',len(observed),'real HTTPS requests verified.')
