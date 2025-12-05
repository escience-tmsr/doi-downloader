// Start a job: open URL in new tab and remember its tabId
function startJob(url, phrase) {
  // First create the tab so we know its id
  browser.tabs.create({ url }).then(tab => {
    const job = {
      url,
      phrase,
      used: false,
      tabId: tab.id
    };

    console.log("[default-plugin] opened initial tab", tab.id, "with URL:", url);

    return browser.storage.local.set({ job });
  }).catch(err => {
    console.error("[default-plugin] error in startJob:", err);
  });
}

// Main listener for messages coming from popup.js and content-script.js
browser.runtime.onMessage.addListener((msg, sender) => {
  if (!msg || !msg.type) {
    return;
  }

  // Called by popup.js to start a new job
  if (msg.type === "start-job") {
    startJob(msg.url, msg.phrase);
    return;
  }

  // Called by content-script.js asking "who am I?"
  if (msg.type === "who-am-i") {
    const tabId = sender && sender.tab ? sender.tab.id : null;
    return Promise.resolve({ tabId });
  }

  // Called by content-script.js to open the second link WITHOUT popup blocking
  if (msg.type === "open-url" && msg.url) {
    console.log("[default-plugin] opening linked URL in new tab:", msg.url);

    return browser.tabs.create({ url: msg.url }).catch(err => {
      console.error("[default-plugin] failed to open new tab:", err);
    });
  }
});
