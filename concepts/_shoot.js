const { chromium, devices } = require('playwright');
const fs = require('fs');
const OUT = '/home/user/workspace/krd/assets/shots';
fs.mkdirSync(OUT, { recursive: true });
const BASE = 'http://127.0.0.1:8777';

const brands = [
  { id: 'apex', detail: '#pricing' },
  { id: 'noir', detail: '#booking' },
  { id: 'evercrest', detail: '#estimate .form' },
];

async function settle(page) {
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    const imgs = Array.from(document.images);
    await Promise.all(imgs.map(i => i.complete ? null : new Promise(r => { i.onload = i.onerror = r; })));
  });
  const bad = await page.evaluate(() => Array.from(document.images).filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src));
  if (bad.length) console.log('  !! images failed:', bad);
  await page.waitForTimeout(700);
}

(async () => {
  const browser = await chromium.launch();
  for (const b of brands) {
    // desktop
    let ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
    let page = await ctx.newPage();
    await page.goto(`${BASE}/${b.id}/index.html`, { waitUntil: 'load' });
    await settle(page);
    // scroll through to trigger any lazy work, then back to top
    await page.evaluate(async () => {
      const h = document.body.scrollHeight;
      for (let y = 0; y < h; y += 700) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
      window.scrollTo(0, 0);
    });
    await settle(page);
    await page.screenshot({ path: `${OUT}/${b.id}-desktop.png` });
    await page.screenshot({ path: `${OUT}/${b.id}-desktop-full.png`, fullPage: true });
    await page.addStyleTag({ content: 'header{position:static !important}' });
    const el = await page.$(b.detail);
    await el.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    await el.screenshot({ path: `${OUT}/${b.id}-detail.png` });
    // overflow check desktop
    const dw = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    console.log(b.id, 'desktop scrollWidth/inner', dw);
    await ctx.close();

    // mobile
    ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1, userAgent: devices['iPhone 13'].userAgent });
    page = await ctx.newPage();
    await page.goto(`${BASE}/${b.id}/index.html`, { waitUntil: 'load' });
    await settle(page);
    await page.evaluate(async () => {
      const h = document.body.scrollHeight;
      for (let y = 0; y < h; y += 700) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
      window.scrollTo(0, 0);
    });
    await settle(page);
    const mw = await page.evaluate(() => {
      const over = [];
      document.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.right > 391.5 || r.left < -1.5) over.push(e.tagName + '.' + e.className + ' ' + Math.round(r.left) + '/' + Math.round(r.right)); });
      return [document.documentElement.scrollWidth, over.slice(0, 12)];
    });
    console.log(b.id, 'mobile scrollWidth', mw[0], 'overflow:', mw[1]);
    await page.screenshot({ path: `${OUT}/${b.id}-mobile.png` });
    await page.screenshot({ path: `${OUT}/${b.id}-mobile-full.png`, fullPage: true });
    await ctx.close();
    console.log('done', b.id);
  }
  await browser.close();
})();
