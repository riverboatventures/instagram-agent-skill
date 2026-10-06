const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }).catch(() => chromium.launch());
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.goto('file://' + __dirname + '/avatar.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  console.log('anton:', await p.evaluate(() => document.fonts.check('100px Anton')));
  await (await p.$('#art')).screenshot({ path: __dirname + '/gta6-profile-picture.png' });
  await b.close();
})();
