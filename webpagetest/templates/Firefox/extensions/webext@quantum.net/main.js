"use strict";
/* globals browser */

console.log('Hello Download');

(function () {
  let downloadId = null;
  let counter = 0;

  function init() {
    console.log('init: ' + counter);
    if (counter++) {
      return;
    }

    browser.downloads.download({
      url: 'http://192.168.1.254:8080/large_file',
      incognito: true,
      filename: 'delete_me.zip',
      conflictAction: 'overwrite',
      saveAs: false
    }).then(id => {
      console.assert(!downloadId);
      downloadId = id;
      console.log('Downloading: ' + downloadId);
    }, err => {
      console.log('Error: ' + err);
    }).catch(exc => {
      console.log('Exception: ' + exc);
      downloadId = null;
    });
  }

  function close() {
    console.log('close: ' + (counter-1));
    if (--counter) {
      return;
    }

    if (downloadId) {
      browser.downloads.cancel(downloadId).then(() => {
        console.log('Canceled Download');
        downloadId = null;
      }, err => {
        console.log('Error: ' + err);
      }).catch(exc => {
        console.log('Exception: ' + exc);
      });
    }
  }

  browser.webNavigation.onBeforeNavigate.addListener(details => {
    console.log('onBeforeNavigate: ' + details.url);
    init();
  });

  browser.webNavigation.onCompleted.addListener(details => {
    console.log('onCompleted: ' + details.url);
    close();
  });

  browser.webNavigation.onErrorOccurred.addListener(details => {
    console.log('onErrorOccurred: ' + details.url);
    close();
  });

})();
