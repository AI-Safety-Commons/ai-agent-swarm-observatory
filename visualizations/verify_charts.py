"""Build the fragment and exercise it in the locally installed headless Chrome."""
import json
import re
import subprocess
import tempfile
import sys
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = os.environ.get('CHROME_BIN') or shutil.which('google-chrome') or shutil.which('chromium') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
subprocess.run([sys.executable, str(HERE.parent / 'build.py')], check=True)
fragment = (HERE / 'wiki-activity.html').read_text()
assert len(fragment.encode()) < 5_000_000
script = '\n'.join(re.findall(r'<script>(.*?)</script>', fragment, re.S))
(HERE / 'check-script.js').write_text(script)
subprocess.run(['node', '--check', str(HERE / 'check-script.js')], check=True)
css = (HERE / 'dashboard.css').read_text()
d3 = (HERE / 'd3-7.9.0.min.js').read_text()
qa_fragment = fragment.replace('<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>', '<script>' + d3 + '</script>')
harness = r'''
<script>
const qaResults=[];
function check(name,value){qaResults.push({name,pass:!!value});}
const el=id=>document.getElementById('wa-'+id);
function change(id,value){el(id).value=value;el(id).dispatchEvent(new Event('change'));}
function total(type){return [...el('timeline').querySelectorAll(`[data-event-type="${type}"]`)].reduce((n,e)=>n+Number(e.dataset.count),0);}
function computedFill(node){return node&&getComputedStyle(node).fill;}
function spacedButtons(nodes){const rects=[...nodes].map(n=>n.getBoundingClientRect());return rects.every(r=>r.height>=44)&&rects.every((a,i)=>rects.slice(i+1).every(b=>Math.max(b.left-a.right,a.left-b.right,b.top-a.bottom,a.top-b.bottom)>=7.9));}
function pieTotal(){return [...el('pie').querySelectorAll('[data-count]')].reduce((n,e)=>n+Number(e.dataset.count),0);}
setTimeout(async()=>{
try {
  check('four rendered charts',document.querySelectorAll('.wa-chart').length===4);
  check('all save records',total(0)===14591);
  check('all deletion events',total(1)===5217);
  check('pie shares cover saves',pieTotal()===14591);
  const dataForColor=JSON.parse(document.getElementById('wa-data').textContent);
  const pageMarks=()=>[...el('timeline').querySelectorAll('[data-category]')];
  const pageGroups=()=>new Set(pageMarks().map(n=>n.dataset.category));
  const pageFills=Object.fromEntries(pageMarks().map(n=>[n.dataset.category,computedFill(n)]));
  check('page color mode is default and wiki mode removed',el('color').value==='page'&&[...el('color').options].map(o=>o.value).join(',')==='page,user,event');
  check('default twenty pages plus Other',el('page-count').value==='20'&&pageGroups().size===21&&pageGroups().has('Other pages'));
  check('page colors are visibly distinct',new Set(Object.values(pageFills)).size===21);
  check('page legend computed colors match marks',[...el('color-legend').querySelectorAll('.wa-color-key')].every(n=>getComputedStyle(n.querySelector('.wa-swatch')).backgroundColor===pageFills[n.textContent]));
  check('page bars computed colors match timeline',[...el('pages').querySelectorAll('[data-page]')].every(n=>computedFill(n)===pageFills[n.dataset.page]));
  check('page names include wiki identity',pageMarks().filter(n=>n.dataset.category!=='Other pages').every(n=>dataForColor.pages.includes(n.dataset.category)));
  check('user selector belongs above pie',el('user-count').closest('section').getAttribute('aria-labelledby')==='wa-users-title'&&el('user-count').getBoundingClientRect().bottom<=el('pie').getBoundingClientRect().top);
  const manifestSaves={dse:13403,probier:1013,fractal:169,dorfwiki:6};
  for(const [i,w] of dataForColor.wikis.entries()){
    change('wiki',String(i));
    check(`${w} dropdown isolates manifest save count`,total(0)===manifestSaves[w]&&pieTotal()===manifestSaves[w]);
    check(`${w} page colors remain stable`,pageMarks().filter(n=>n.dataset.category!=='Other pages'&&pageFills[n.dataset.category]).every(n=>computedFill(n)===pageFills[n.dataset.category]));
  }
  change('wiki','all');
  check('page limits offer all supported counts',['5','10','20','50','100'].every(v=>[...el('page-count').options].some(o=>o.value===v)));
  for(const count of [5,10,50,100]){
    change('page-count',String(count));
    check(`top${count} page groups preserve population`,pageGroups().size===count+1&&pageGroups().has('Other pages')&&total(0)===14591&&total(1)===5217);
  }
  check('page limit leaves user selection unchanged',el('user-count').value==='10'&&el('pie').querySelectorAll('[data-label]').length===11);
  change('page-count','20');
  change('from','2030-01-01');change('to','2030-01-02');
  check('empty dates render no page groups',pageGroups().size===0&&total(0)===0);
  change('from',dataForColor.dates[0]);change('to',dataForColor.dates.at(-1));
  document.querySelector('[data-type="0"]').click();document.querySelector('[data-type="1"]').click();
  check('empty event selection renders no page groups',pageGroups().size===0);
  document.querySelector('[data-type="0"]').click();document.querySelector('[data-type="1"]').click();
  check('event buttons have 44px height and 8px separation',spacedButtons(el('series').querySelectorAll('button')));
  check('no conflicting event color key',[...el('series').querySelectorAll('.wa-legend .wa-swatch')].every(n=>getComputedStyle(n).display==='none'));
  check('ten named slices plus other',el('pie').querySelectorAll('[data-label]').length===11);
  check('ten distinct label colors',new Set([...el('pie').querySelectorAll('[data-label]')].map(n=>n.getAttribute('fill'))).size===11);
  const colorBefore=el('pie').querySelector('[data-label="AgentRelent"]').getAttribute('fill');
  change('color','user');
  check('page limit hidden for user mode',getComputedStyle(el('page-count-field')).display==='none');
  check('user split preserves populations',total(0)===14591&&total(1)===5217);
  check('same user color across charts',el('timeline').querySelector('[data-category="AgentRelent"]').getAttribute('fill')===colorBefore);
  change('color','event');check('event color mode preserves totals',total(0)===14591&&total(1)===5217);
  check('event color key visible',[...el('series').querySelectorAll('.wa-legend .wa-swatch')].every(n=>getComputedStyle(n).display!=='none'));
  change('color','page');
  check('page limit visible in page mode',getComputedStyle(el('page-count-field')).display!=='none');
  change('user-count','20');check('twenty named slices',el('pie').querySelectorAll('[data-label]').length===21&&pieTotal()===14591);
  change('user-count','5');check('five named slices',el('pie').querySelectorAll('[data-label]').length===6&&pieTotal()===14591);
  change('user-count','50');check('fifty named slices',el('pie').querySelectorAll('[data-label]').length===51&&pieTotal()===14591);
  change('user-count','100');check('one hundred named slices plus other preserve total',el('pie').querySelectorAll('[data-label]').length===101&&pieTotal()===14591);
  check('user limit leaves page selection unchanged',el('page-count').value==='20'&&pageGroups().size===21);
  check('user count offers all supported limits',['5','10','20','50','100'].every(v=>[...el('user-count').options].some(o=>o.value===v)));
  const firstPage=el('users').textContent,firstStatus=el('user-page').textContent;
  check('top100 begins with ten named rows and separate Other',el('users').children.length===10&&el('other').children.length===1&&el('other').textContent.includes('Other')&&el('user-prev').disabled&&!el('user-next').disabled);
  check('pagination buttons have 44px height and 8px separation',spacedButtons([el('user-prev'),el('user-next')]));
  el('user-next').click();check('next page changes ten names and page status',el('users').children.length===10&&el('users').textContent!==firstPage&&el('user-page').textContent!==firstStatus&&!el('user-prev').disabled);
  el('user-prev').click();check('previous page restores names and status',el('users').textContent===firstPage&&el('user-page').textContent===firstStatus&&el('user-prev').disabled);
  const visitedNames=[];
  for(let page=0;page<10;page++){
    check(`top100 page ${page+1} contains ten names`,el('users').children.length===10);
    visitedNames.push(...[...el('users').children].map(row=>row.cells[0].textContent.trim()));
    if(page<9)el('user-next').click();
  }
  check('top100 ends after 100 unique named rows',new Set(visitedNames).size===100&&el('user-next').disabled&&!el('user-prev').disabled&&el('other').children.length===1);
  change('color','user');
  check('top100 user timeline retains both event populations',total(0)===14591&&total(1)===5217);
  check('top100 user timeline has 100 names plus remainder',new Set([...el('timeline').querySelectorAll('[data-category]')].map(n=>n.dataset.category)).size===101);
  change('user-count','10');
  check('count change resets pagination to first ten',el('users').children.length===10&&el('users').textContent===firstPage&&el('user-prev').disabled&&el('user-next').disabled&&el('pie').querySelectorAll('[data-label]').length===11);
  check('count change updates user timeline to ten plus remainder',new Set([...el('timeline').querySelectorAll('[data-category]')].map(n=>n.dataset.category)).size===11&&total(0)===14591&&total(1)===5217);
  change('color','page');
  change('wiki',String(dataForColor.wikis.indexOf('dse')));
  check('label color stable across wiki filters',el('pie').querySelector('[data-label="AgentRelent"]').getAttribute('fill')===colorBefore);
  change('wiki','all');
  check('68 recreation relations',el('recreate-detail').textContent.startsWith('68 '));
  change('from','2026-06-18');change('to','2026-06-18');
  check('June 18 saves',total(0)===6543);
  const d=JSON.parse(document.getElementById('wa-data').textContent);
  change('wiki',String(d.wikis.indexOf('probier')));
  check('wiki filter on peak day',total(0)===d.rows.filter(r=>d.dates[r[0]]==='2026-06-18'&&d.wikis[r[1]]==='probier'&&r[2]===0).reduce((n,r)=>n+r[5],0));
  change('from',d.dates[0]);change('to',d.dates.at(-1));
  check('probier saves',total(0)===1013&&pieTotal()===1013);
  change('measure','1');check('empty deletion pie',el('pie').textContent.includes('No matching'));
  change('wiki','all');check('deletion pie',pieTotal()===5217);
  change('measure','3');check('recovery pie',pieTotal()===4);
  document.querySelector('[data-type="2"]').click();check('probe toggle',total(2)===101);
  check('probes remain explicitly unattributed to pages',[...el('timeline').querySelectorAll('[data-event-type="2"]')].every(n=>n.dataset.category==='No page attribution')&&pageMarks().filter(n=>n.dataset.category==='No page attribution').reduce((n,e)=>n+Number(e.dataset.count),0)===101);
  document.querySelector('[data-type="0"]').click();check('save toggle hides marks',el('timeline').querySelectorAll('[data-event-type="0"]').length===0);
  document.querySelector('[data-type="0"]').click();document.querySelector('[data-type="2"]').click();
  change('from','2026-07-14');change('to','2026-05-17');check('invalid dates flagged',!el('error').hidden);
  change('from',d.dates[0]);change('to',d.dates.at(-1));change('measure','0');
  const hit=el('timeline').querySelector('[data-chart-hit]'),b=hit.getBoundingClientRect();
  hit.dispatchEvent(new PointerEvent('pointermove',{clientX:b.x+b.width/2,clientY:b.y+30,bubbles:true}));
  check('timeline tooltip',!document.querySelector('.wa-tip').hidden&&document.querySelector('.wa-tip').textContent.includes('Saved revisions'));
  hit.dispatchEvent(new MouseEvent('click',{clientX:b.x+b.width/2,clientY:b.y+30,bubbles:true}));
  check('day click detail',el('day').textContent.includes('Saved revisions'));
  hit.dispatchEvent(new PointerEvent('pointerleave'));
  check('axes quantities and units',document.querySelectorAll('text.axis-title[data-axis="x"]').length===3&&document.querySelectorAll('text.axis-title[data-axis="y"]').length===3);
  const timelineHost=el('timeline'),panel=timelineHost.closest('.wa-panel'),panelStyle=getComputedStyle(panel);
  check('chart fits panel width',Math.abs(timelineHost.getBoundingClientRect().width-(panel.clientWidth-parseFloat(panelStyle.paddingLeft)-parseFloat(panelStyle.paddingRight)))<1);
  check('no horizontal overflow',document.getElementById('wiki-activity').scrollWidth<=window.qaWidth);
  check('visible labels >= 11px',[...document.querySelectorAll('.wa-chart text')].every(n=>parseFloat(getComputedStyle(n).fontSize)>=11));
  change('user-count','100');change('color','page');change('page-count','20');
  check('top100 layout has no horizontal overflow',document.getElementById('wiki-activity').scrollWidth<=window.qaWidth);
  check('samples do not require a load button',el('sample-load').hidden);
  for(let i=0;i<200&&el('sample-browser').hidden&&el('sample-error').hidden;i++)await new Promise(resolve=>setTimeout(resolve,20));
  const sampleCount=()=>Number(el('sample-results').dataset.matchCount);
  const sampleInput=(id,value)=>{el('sample-'+id).value=value;el('sample-'+id).dispatchEvent(new Event(id==='user'||id==='page'?'input':'change'));};
  check('all saved revision samples load automatically offline',!el('sample-browser').hidden&&sampleCount()===14591);
  const summaries=JSON.parse(document.getElementById('wa-summary-data').textContent).summaries;
  check('twenty precomputed summaries available',summaries.length===20&&el('summary-user').options.length===20);
  check('summary paragraphs match the cached output',summaries.every(s=>{change('summary-user',s.label);return el('summary-paragraph').textContent===s.paragraph;}));
  change('summary-user','AgentRelent');
  const retainedSummary=el('summary-paragraph').textContent;
  change('from','2026-06-18');change('to','2026-06-18');check('summary scope remains whole-export under chart date filters',el('summary-paragraph').textContent===retainedSummary);
  change('from',d.dates[0]);change('to',d.dates.at(-1));
  const tableLink=el('users').querySelector('[data-summary-label="AgentRelent"]');
  check('named table labels link to summaries with usable targets',!!tableLink&&tableLink.getBoundingClientRect().height>=44);
  change('summary-user','AgentHelperTwo');tableLink.click();check('table label selects its own summary',el('summary-user').value==='AgentRelent'&&el('summary-paragraph').textContent===retainedSummary);
  check('blank and Other buckets have no summary links',![...el('users').querySelectorAll('[data-summary-label]')].some(n=>n.dataset.summaryLabel==='(blank label)')&&el('other').querySelectorAll('[data-summary-label]').length===0);
  el('summary-details').open=true;
  let linkedEvidence=0;
  for(const summary of summaries){
    change('summary-user',summary.label);
    for(let i=0;i<summary.evidence.length;i++){
      const ref=summary.evidence[i];el('summary-evidence').querySelector(`[data-summary-evidence="${i}"]`).click();
      for(let n=0;n<20&&!el('summary-status').textContent.startsWith('Opened ');n++)await new Promise(resolve=>setTimeout(resolve,10));
      const target=[...el('sample-results').querySelectorAll('details')].find(n=>n.dataset.revision===`${ref.page}@${ref.seq}`);
      if(target&&target.open&&el('sample-user').value===summary.label&&el('sample-page').value===ref.page&&el('sample-from').value===ref.time.slice(0,10)&&el('sample-to').value===ref.time.slice(0,10))linkedEvidence++;
    }
  }
  check('all sixty evidence buttons open the exact revision',linkedEvidence===60);
  check('summary text rendered as plain text',el('summary-paragraph').children.length===0);
  check('summary evidence buttons are spaced for touch',spacedButtons(el('summary-evidence').querySelectorAll('button')));
  change('summary-user','ResearchHelper');el('summary-details').open=false;el('sample-reset').click();
  check('only ten sample records rendered',el('sample-results').querySelectorAll('details').length===10);
  const firstSamples=[...el('sample-results').querySelectorAll('details')].map(n=>n.dataset.revision).join('|');
  el('sample-next').click();check('sample pagination advances',el('sample-page-status').textContent.startsWith('11–20')&&[...el('sample-results').querySelectorAll('details')].map(n=>n.dataset.revision).join('|')!==firstSamples);
  el('sample-prev').click();check('sample pagination returns',el('sample-page-status').textContent.startsWith('1–10'));
  sampleInput('from','2026-06-18');sampleInput('to','2026-06-18');check('sample UTC date range includes whole day',sampleCount()===6543);
  sampleInput('from','2026-06-19');check('invalid sample dates clear results',!el('sample-error').hidden&&sampleCount()===0);
  el('sample-reset').click();sampleInput('user','AgentRelent');check('sample exact user filter',sampleCount()===317);
  sampleInput('user','unmatched-user-qa-zzzz');check('empty sample state',sampleCount()===0&&el('sample-results').textContent.includes('No saved revisions'));
  el('sample-reset').click();
  sampleInput('wiki',String(d.wikis.indexOf('dorfwiki')));check('sample wiki filter',sampleCount()===6);
  sampleInput('user','dataresearcheralpha');check('case-insensitive sample user search',sampleCount()===2);
  sampleInput('page','dorfwiki/AgentDataUSAProbeFebX2');sampleInput('from','2026-06-22');sampleInput('to','2026-06-22');
  check('combined sample filters intersect',sampleCount()===2);
  const sampleDetails=el('sample-results').querySelector('details');sampleDetails.open=true;
  check('sample revision text is readable and inert',el('sample-results').querySelector('pre').textContent.includes('Test links public Data USA research')&&el('sample-results').querySelector('pre').children.length===0);
  check('sample filtering leaves charts unchanged',total(0)===14591);
  check('small sample result disables next',el('sample-next').disabled);
  sampleInput('page','__missing_page_qa__');check('sample page no-match filter',sampleCount()===0);
  el('sample-reset').click();change('wiki',String(d.wikis.indexOf('probier')));check('chart filtering leaves samples unchanged',sampleCount()===14591);
  change('wiki','all');
  check('sample controls have safe spacing',spacedButtons([el('sample-prev'),el('sample-next')]));
  check('loaded sample layout has no horizontal overflow',document.getElementById('wiki-activity').scrollWidth<=window.qaWidth);
  check('requested appearance is applied',getComputedStyle(document.documentElement).colorScheme===window.qaTheme);
  sampleInput('page','dse/TmpJan18HtmlHost987');
  check('real HTML-bearing sample stays literal',sampleCount()>0&&/<script|<img/i.test(el('sample-results').textContent)&&el('sample-results').querySelectorAll('script,img,iframe').length===0);
  check('excerpt containers never create child markup',[...el('sample-results').querySelectorAll('pre')].every(n=>n.children.length===0));
  sampleInput('wiki',String(d.wikis.indexOf('dorfwiki')));sampleInput('page','dorfwiki/AgentDataUSAProbeFebX2');el('sample-results').querySelector('details').open=true;
  check('no runtime errors',!window.qaErrors.length);
}catch(e){qaResults.push({name:'runtime exception',pass:false,error:String(e)});}
const report=document.createElement('script');report.id='qa-results';report.type='application/json';report.textContent=JSON.stringify({tests:qaResults,errors:window.qaErrors});document.body.append(report);
},100);
</script>
'''
results = []
for width, theme in [(360, 'light'), (1024, 'light'), (736, 'light'), (736, 'dark'), (360, 'dark')]:
    if len(sys.argv)>1 and str(width) not in sys.argv[1:]:
        continue
    name = f'qa-{width}-{theme}'
    document = f'<!doctype html><html data-visualize-standalone lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>{css}</style></head><body><script>window.qaWidth={width};window.qaTheme="{theme}";window.qaErrors=[];window.onerror=(m)=>window.qaErrors.push(String(m));</script>{qa_fragment}<style>:root{{color-scheme:{theme};width:{width}px}}body{{width:{width}px}}</style>{harness}</body></html>'
    path = HERE / f'{name}.html'
    path.write_text(document)
    with tempfile.TemporaryDirectory(prefix='wiki-chart-qa-') as profile:
        command = [CHROME, '--headless', '--disable-gpu', '--disable-background-networking', '--disable-component-update', '--disable-extensions', '--no-first-run', '--no-default-browser-check', f'--user-data-dir={profile}', '--hide-scrollbars', f'--window-size={width},5800', '--virtual-time-budget=10000', f'--screenshot={HERE / (name + ".png")}', '--dump-dom', path.as_uri()]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            stdout, _ = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, _ = proc.communicate(timeout=5)
        output = stdout.decode(errors='replace')
        match = re.search(r'<script id="qa-results" type="application/json">(.*?)</script>', output, re.S)
        result = json.loads(match.group(1)) if match else {'tests': [], 'errors': ['No browser test results']}
        result.update(width=width, theme=theme)
        results.append(result)
        print(name, json.dumps(result), flush=True)
report_path=HERE / 'verification.json'
if len(sys.argv)>1 and report_path.exists():
    previous=json.loads(report_path.read_text())
    results=[r for r in previous if str(r['width']) not in sys.argv[1:]]+results
report_path.write_text(json.dumps(results, indent=2))
assert all(r['tests'] and not r['errors'] and all(t['pass'] for t in r['tests']) for r in results)
