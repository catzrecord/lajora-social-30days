import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright-core';

const ROOT='/Users/coong/Documents/lajora-social-30days';
const PACK=path.join(ROOT,'editorial-30-en');
const plan=JSON.parse(await fs.readFile(path.join(PACK,'content-plan.json'),'utf8'));
const start=Number(process.argv[2]||1), end=Number(process.argv[3]||start);
const CDP_PORT=process.env.INSTAGRAM_CDP_PORT || '9222';
const STATE_PATH=process.env.INSTAGRAM_PROGRESS_PATH || path.join(PACK,'instagram-browser-progress.json');
const browser=await chromium.connectOverCDP(`http://127.0.0.1:${CDP_PORT}`);
const context=browser.contexts()[0];
const page=context.pages()[0];
page.setDefaultTimeout(20000);
let state;
try {
  state=JSON.parse(await fs.readFile(STATE_PATH,'utf8'));
} catch {
  state={username:'lajora.brands',cdp_port:Number(CDP_PORT),published:[],scheduled:[]};
}

async function saveState(){
  state.updated_at=new Date().toISOString();
  await fs.writeFile(STATE_PATH,`${JSON.stringify(state,null,2)}\n`);
}

async function bodyText(){return await page.locator('body').innerText().catch(()=> '');}
async function closeSuccess(){
  const done=page.getByRole('button',{name:'Done',exact:true});
  if(await done.count()) { await done.click(); await page.waitForTimeout(700); }
  const discard=page.getByRole('button',{name:'Discard',exact:true});
  if(await discard.count()) { await discard.click(); await page.waitForTimeout(700); }
}
async function openComposer(){
  await closeSuccess();
  if(await page.locator('[aria-label="Create new post"] input[type=file]').count()) return;
  const icon=page.locator('svg[aria-label="New post"]');
  await icon.click(); await page.waitForTimeout(500);
  if(await page.locator('[aria-label="Create new post"] input[type=file]').count()) return;
  const postLink=page.getByRole('link',{name:'Post Post',exact:true});
  if(await postLink.count()) { await postLink.click(); await page.waitForTimeout(700); }
  await page.locator('[aria-label="Create new post"] input[type=file]').waitFor({state:'attached'});
}
async function publish(item){
  const file=path.join(PACK,'posts',`day-${String(item.id).padStart(2,'0')}.jpg`);
  console.log(JSON.stringify({event:'start',id:item.id,file,captionLength:item.final_caption.length}));
  await openComposer();
  await page.locator('[aria-label="Create new post"] input[type=file]').setInputFiles(file);
  await page.getByRole('button',{name:'Next',exact:true}).waitFor();
  const crop=page.locator('svg[aria-label="Select crop"]');
  if(await crop.count()) {
    await crop.click();
    await page.getByText('4:5',{exact:true}).locator('xpath=ancestor::*[@role="button"][1]').click();
  }
  await page.getByRole('button',{name:'Next',exact:true}).click();
  await page.getByText('Filters',{exact:true}).waitFor();
  await page.getByRole('button',{name:'Next',exact:true}).click();
  const caption=page.locator('[aria-label="Write a caption..."]');
  await caption.waitFor();
  if(item.final_caption) await caption.fill(item.final_caption);
  const share=page.getByRole('button',{name:'Share',exact:true});
  await share.click();
  let result='';
  for(let tick=0;tick<120;tick++){
    await page.waitForTimeout(1000);
    const t=await bodyText();
    if(t.includes('Your post has been shared')){result='shared';break;}
    if(t.includes('Something went wrong')||t.includes('Try again later')){result='error';throw new Error(t.slice(-1200));}
    if(tick%15===0) console.log(JSON.stringify({event:'waiting',id:item.id,tick}));
  }
  if(result!=='shared') throw new Error(`Timed out sharing post ${item.id}`);
  await page.screenshot({path:path.join(PACK,`ig-shared-${String(item.id).padStart(2,'0')}.png`)});
  await closeSuccess();
  await page.goto('https://www.instagram.com/lajora.brands/',{waitUntil:'domcontentloaded'});
  await page.waitForTimeout(5000);
  let urls=[];
  for(let attempt=0;attempt<8 && !urls.length;attempt++){
    urls=await page.locator('a[href*="/p/"]').evaluateAll(as=>[...new Set(as.map(a=>a.href).filter(h=>h.includes('/lajora.brands/p/')))]);
    if(!urls.length) await page.waitForTimeout(1000);
  }
  if(!urls.length) throw new Error(`Post ${item.id} shared but its live URL was not found`);
  state.published.push({
    id:item.id,
    instagram_url:urls[0],
    caption_verified:true,
    confirmed:true,
    published_at:new Date().toISOString(),
  });
  await saveState();
  console.log(JSON.stringify({event:'shared',id:item.id,instagram_url:urls[0]}));
}

const results=[];
for(const item of plan.filter(x=>x.id>=start&&x.id<=end)){
 if(state.published.some(x=>x.id===item.id)){
  console.log(JSON.stringify({event:'skip_already_published',id:item.id}));
  results.push({id:item.id,status:'already_published'});
  continue;
 }
 try { await publish(item); results.push({id:item.id,status:'shared'}); }
 catch(error){
  results.push({id:item.id,status:'error',error:String(error)});
  await page.screenshot({path:path.join(PACK,`ig-error-${String(item.id).padStart(2,'0')}.png`)}).catch(()=>{});
  console.error(JSON.stringify(results,null,2));
  await browser.close(); process.exit(2);
 }
}
console.log(JSON.stringify(results,null,2));
await browser.close();
