const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('file://' + __dirname + '/test_grid.html');
  const heights = await page.evaluate(() => {
    return {
      restricted: document.querySelector('.modal-grid').offsetHeight,
      tall: document.querySelector('.modal-grid-tall').offsetHeight
    };
  });
  console.log(heights);
  await browser.close();
})();
