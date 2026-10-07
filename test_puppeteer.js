const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 600 });
  
  // Go to local dev server (wait, preview server is running on 5173!)
  await page.goto('http://localhost:5173/people', { waitUntil: 'networkidle0' });
  
  // Click "Add person"
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const addBtn = btns.find(b => b.innerText.includes('Add person'));
    if (addBtn) addBtn.click();
  });
  
  await page.waitForTimeout(1000);
  
  // Get ModalBody scrollHeight and clientHeight
  const stats = await page.evaluate(() => {
    const body = document.querySelector('.overflow-y-auto');
    if (!body) return 'No ModalBody found';
    return {
      scrollHeight: body.scrollHeight,
      clientHeight: body.clientHeight,
      height: body.getBoundingClientRect().height,
      canScroll: body.scrollHeight > body.clientHeight,
      html: body.outerHTML.substring(0, 500)
    };
  });
  
  console.log(stats);
  await browser.close();
})();
