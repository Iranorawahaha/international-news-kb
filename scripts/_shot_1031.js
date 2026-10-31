const puppeteer = require('puppeteer-core');
const path = require('path');
(async () => {
  const BASE = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50';
  const file = 'file://' + path.resolve(BASE + '/diplomatic-affairs.html');
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-gpu'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1180, height: 1400, deviceScaleFactor: 2 });
  await page.goto(file, { waitUntil: 'load', timeout: 60000 });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: BASE + '/diplomatic-affairs-1031-top.png', clip: { x: 0, y: 0, width: 1180, height: 1700 } });
  await page.screenshot({ path: BASE + '/diplomatic-affairs-1031-full.png', fullPage: true });
  console.log('done');
  await browser.close();
})();
