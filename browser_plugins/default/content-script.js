console.log("[default-extension] content-script injected on", window.location.href);

browser.runtime.sendMessage({ type: "what-is-my-tabid" })
  .then(response => {
    const myTabId = response && response.tabId;
    console.log("[default-extension] my tabId is", myTabId);
    if (myTabId != null) {
      window.setTimeout(() => maybeRunJob(myTabId), 500);
    } else {
      console.log("[default-extension] no tabId available, doing nothing");
    }
  })
  .catch(err => {
    console.error("[default-extension] error getting tabId:", err);
  });
