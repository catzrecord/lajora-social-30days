import { chromium } from 'playwright-core';
import fs from 'node:fs/promises';
const codes=['Dba7qBKFCg3','Dba7k2zFOeq','Dba7gQylOIV','Dba7a5nlDab','Dba7WGIlA3r','Dba7RyRlAsC','Dba7NGhlJYc','Dba7I6UlB-j','Dba7DQylP6q'];
const browser=await chromium.connectOverCDP('http://127.0.0.1:9224');
const page=browser.contexts()[0].pages()[0];page.setDefaultTimeout(30000);
const deleted=[];
for(const code of codes){
 const url=`https://www.instagram.com/lajora.brands/p/${code}/`;
 console.log('open',url);
 await page.goto(url,{waitUntil:'domcontentloaded'});await page.waitForTimeout(4500);
 if((await page.locator('body').innerText()).includes("Sorry, this page isn't available")){console.log('already gone',code);deleted.push(code);continue;}
 const more=page.locator('svg[aria-label="More options"]');await more.waitFor();await more.click();
 await page.getByText('Delete',{exact:true}).click();
 await page.getByText('Delete post?',{exact:true}).waitFor();
 await page.getByText('Delete',{exact:true}).click();
 for(let i=0;i<30;i++){await page.waitForTimeout(500);if(!await page.getByText('Delete post?',{exact:true}).count())break;}
 deleted.push(code);console.log('deleted',code);
}
await page.goto('https://www.instagram.com/lajora.brands/',{waitUntil:'domcontentloaded'});await page.waitForTimeout(6000);
const body=await page.locator('body').innerText();const countLine=body.split('\n').find(x=>/^\d+ posts$/.test(x))||'';
const urls=await page.locator('a[href*="/p/"]').evaluateAll(as=>[...new Set(as.map(a=>a.href).filter(h=>h.includes('/lajora.brands/p/')))]);
await page.evaluate(()=>scrollTo(0,430));await page.waitForTimeout(1000);
await page.screenshot({path:'/Users/coong/Documents/lajora-social-30days/editorial-30-en/live-instagram-grid-final-2026-07-31.png'});
await fs.writeFile('/Users/coong/Documents/lajora-social-30days/editorial-30-en/deleted-superseded-posts.json',JSON.stringify({deleted,countLine,urls,verified_at:new Date().toISOString()},null,2)+'\n');
console.log(JSON.stringify({deleted:deleted.length,countLine,urls},null,2));
await browser.close();
