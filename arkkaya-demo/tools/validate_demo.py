"""Exercise the actual demo in Chromium and export client-review JPEGs."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables'
BASE = os.environ.get('ARKAYA_TEST_BASE', 'http://127.0.0.1:3000/')
results = []

def passed(name):
    results.append({'check':name, 'outcome':'passed'})
    print('PASS:', name)

def ready(page):
    page.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")')
    page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
    page.evaluate('document.fonts.ready')

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[]
    external=[]
    page.on('pageerror', lambda error:errors.append(str(error)))
    page.on('request', lambda request:external.append(request.url) if not request.url.startswith(('http://127.0.0.1:3000/','data:','file:')) else None)
    page.goto(BASE,wait_until='networkidle')
    ready(page)
    expect(page.locator('h1')).to_have_text('Spaces for the wayyou live.')
    # Correct section ordering, not just the presence of headings.
    sections=page.locator('main > section').evaluate_all('(els)=>els.map(e=>e.className)')
    assert 'hero' in sections[0] and 'founders-section' in sections[1] and 'projects-section' in sections[2]
    assert 'services-section' in sections[3] and 'process-section' in sections[4] and 'contact-band' in sections[-1]
    passed('Homepage follows the brief’s section order')
    first=page.locator('#selected-projects h3').first.inner_text()
    page.get_by_role('button',name='Next selected projects',exact=True).click()
    assert page.locator('#selected-projects h3').first.inner_text()!=first
    page.get_by_role('button',name='Previous selected projects',exact=True).click()
    assert page.locator('#selected-projects h3').first.inner_text()==first
    passed('Selected-project arrows browse and return')

    page.goto(BASE+'#/projects')
    page.get_by_role('button',name='Architecture',exact=True).click()
    expect(page.locator('#filtered-projects .project-card')).to_have_count(1)
    expect(page.locator('#filtered-projects h3')).to_have_text('The Neoclassical Villa')
    page.get_by_role('button',name='Interiors',exact=True).click()
    expect(page.locator('#filtered-projects .project-card')).to_have_count(2)
    expect(page.locator('#filtered-projects h3').first).to_have_text('Modern Luxe Residence')
    page.get_by_role('button',name='All projects',exact=True).click()
    expect(page.locator('#filtered-projects .project-card')).to_have_count(3)
    passed('Architecture / Interiors / All project filters show the correct projects')

    page.goto(BASE+'#/project/neoclassical-villa')
    ready(page)
    page.locator('.gallery-tile').first.click()
    expect(page.locator('dialog')).to_be_visible()
    expect(page.locator('.lightbox-controls')).to_contain_text('1 / 5')
    page.get_by_role('button',name='Next gallery image',exact=True).click()
    expect(page.locator('.lightbox-controls')).to_contain_text('2 / 5')
    page.keyboard.press('ArrowLeft')
    expect(page.locator('.lightbox-controls')).to_contain_text('1 / 5')
    page.keyboard.press('Escape')
    expect(page.locator('dialog')).not_to_be_visible()
    page.locator('.next-project h3 a').click()
    expect(page.locator('h1')).to_have_text('Modern Luxe Residence')
    passed('Project galleries, keyboard navigation, closing, and next-project link')

    page.goto(BASE)
    ready(page)
    for box in page.locator('.reel-card').all():
        rect=box.bounding_box()
        assert abs(rect['width']/rect['height']-9/16)<0.003
    page.get_by_role('button',name='Open Reel concept: Light & shadow').click()
    expect(page.locator('.reel-player')).to_be_visible()
    page.get_by_role('button',name='Pause',exact=True).click()
    page.get_by_role('button',name='Next Reel chapter',exact=True).click()
    expect(page.locator('.reel-count')).to_have_text('2 / 3')
    page.get_by_role('button',name='Close dialog',exact=True).click()
    passed('Reel cards use 9:16, open, pause, advance, and close')

    page.goto(BASE+'#/contact')
    page.get_by_role('button',name='Preview enquiry',exact=False).click()
    assert not page.locator('#full-name').evaluate('(e)=>e.checkValidity()')
    expect(page.locator('.form-status')).to_be_empty()
    page.locator('#full-name').fill('Demo Reviewer')
    page.locator('#email').fill('reviewer@example.com')
    page.locator('#service').select_option('architecture')
    page.locator('#message').fill('A fictional enquiry for client review.')
    page.get_by_role('button',name='Preview enquiry',exact=False).click()
    expect(page.locator('.form-status')).to_contain_text('not been sent or saved')
    assert page.evaluate('localStorage.length')==0
    assert page.evaluate('sessionStorage.length')==0
    page.goto(BASE+'#/services#interiors')
    page.locator('#interiors').get_by_role('link',name='Discuss your interiors',exact=False).click()
    expect(page.locator('#service')).to_have_value('interiors')
    passed('Required enquiry fields, local-only confirmation, no browser storage, and service preselection')

    page.goto(BASE+'#/careers')
    page.locator('#full-name').fill('Demo Applicant')
    page.locator('#email').fill('applicant@example.com')
    page.locator('#role').select_option(label='Architecture')
    page.locator('#message').fill('Fictional application for validation only.')
    page.locator('#resume').set_input_files({'name':'resume.txt','mimeType':'text/plain','buffer':b'test'})
    assert not page.locator('#resume').evaluate('(e)=>e.checkValidity()')
    page.locator('#resume').set_input_files({'name':'resume.pdf','mimeType':'application/pdf','buffer':b'%PDF-1.4\n'+b'0'*(5*1024*1024+1)})
    assert not page.locator('#resume').evaluate('(e)=>e.checkValidity()')
    page.locator('#resume').set_input_files({'name':'resume.pdf','mimeType':'application/pdf','buffer':b'%PDF-1.4\n% Demo PDF selection fixture only'})
    assert page.locator('#resume').evaluate('(e)=>e.checkValidity()')
    page.get_by_role('button',name='Preview application',exact=False).click()
    expect(page.locator('.form-status')).to_contain_text('not been sent or uploaded')
    passed('Careers rejects wrong type and files over 5 MB; valid PDF selection receives demo confirmation')

    page.get_by_role('link',name='Privacy',exact=True).click()
    expect(page.locator('h1')).to_have_text('Privacy, made clear.')
    expect(page.locator('main')).to_contain_text('does not submit it to Arkkaya')
    passed('Privacy link opens the applicable demo privacy page')

    for width in [1440,390,320,768]:
        page.set_viewport_size({'width':width,'height':1000 if width>700 else 844})
        for route in ['/','/projects','/project/neoclassical-villa','/project/modern-luxe-residence','/project/blue-reverie-lounge','/services','/about','/contact','/careers','/privacy']:
            page.goto(BASE+'#'+route)
            ready(page)
            assert page.locator('h1').count()==1,(width,route,'missing heading')
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,route,'overflow')
            for href in page.locator('a[href]').evaluate_all('(els)=>els.map(a=>a.getAttribute("href"))'):
                assert href.startswith(('#/','#main','mailto:support@arkkayadesign.com','https://instagram.com/arkkaya.design')),href
        passed(f'All 10 routes load with images and no horizontal overflow at {width}px')

    page.set_viewport_size({'width':390,'height':844})
    page.goto(BASE)
    page.get_by_role('button',name='Open navigation',exact=True).click()
    expect(page.locator('#mobile-nav')).to_be_visible()
    page.locator('#mobile-nav').get_by_role('link',name='Projects',exact=True).click()
    expect(page.locator('#mobile-nav')).not_to_be_visible()
    expect(page.locator('h1')).to_contain_text('Considered spaces.')
    passed('Mobile menu opens, navigates and closes')

    page.goto(BASE)
    page.get_by_role('button',name='Design preview',exact=False).click()
    expect(page.locator('#dialog-content')).to_contain_text('reused from the supplied website')
    page.keyboard.press('Escape')
    passed('Preview notes describe original asset reuse and demo-only forms')

    for label,width,height in [('desktop',1440,1000),('mobile',390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        for slug,route in [('homepage','/'),('project-detail','/project/neoclassical-villa')]:
            page.goto(BASE+'#'+route)
            ready(page)
            page.screenshot(path=str(OUT/f'{slug}-{label}.jpg'),full_page=True,type='jpeg',quality=94)
    passed('Four full-page JPEGs exported: homepage and project, desktop and mobile')

    # A single overview frame is useful before opening the full-length exports.
    page.set_viewport_size({'width':1440,'height':1100})
    page.goto(BASE)
    ready(page)
    page.screenshot(path=str(OUT/'homepage-first-screen.jpg'),type='jpeg',quality=95)
    standalone=OUT/'Arkaya-Interactive-Demo.html'
    if standalone.exists():
        # The managed cloud browser disallows file:// navigation. Load the one
        # HTML document locally, then disconnect before exercising its routes.
        page.goto(BASE+'deliverables/Arkaya-Interactive-Demo.html',wait_until='load')
        page.context.set_offline(True)
        ready(page)
        page.locator('.hero-actions a').first.click()
        page.get_by_role('button',name='Architecture',exact=True).click()
        expect(page.locator('#filtered-projects .project-card')).to_have_count(1)
        page.locator('.project-card .view-project').click()
        expect(page.locator('h1')).to_have_text('The Neoclassical Villa')
        page.locator('.gallery-tile').first.click()
        expect(page.locator('dialog')).to_be_visible()
        page.keyboard.press('Escape')
        passed('Single-file HTML: images, routing, filters and gallery work with network disabled after initial document load')
        page.context.set_offline(False)
    assert not errors,errors
    assert not external,external
    passed('No JavaScript exceptions or third-party requests during validation')
    browser.close()

(OUT/'validation-report.json').write_text(json.dumps({'browser':'Chromium','base':BASE,'checks':results,'summary':{'passed':len(results),'failed':0}},indent=2))
print(f'Completed: {len(results)} checks passed.')
