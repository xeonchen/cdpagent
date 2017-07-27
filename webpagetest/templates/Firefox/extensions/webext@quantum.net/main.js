"use strict";
/* globals browser */

console.log('Hello Tabs');

(function() {
  let counter = 10;

  const URLs = [
    'https://www.google.com.tw/search?q=mozilla',
    'https://www.youtube.com/watch?v=tRlmP6xWdw0',
    'https://www.facebook.com/mozilla',
    'http://www.baidu.com/s?wd=謀智',
    'https://en.wikipedia.org/wiki/Mozilla',
    'https://yahoo.com/',
    'http://www.qq.com',
    'https://www.reddit.com/r/mozilla/',
    'https://www.amazon.com',
    'https://world.taobao.com'
  ];

  function openBackgroundTab() {
    if (counter <= 0) {
      return;
    }
    --counter;

    browser.tabs.create({
      url: URLs[counter],
      active: false
    });
  }

  browser.webNavigation.onBeforeNavigate.addListener(details => {
    openBackgroundTab();
  });

})();

