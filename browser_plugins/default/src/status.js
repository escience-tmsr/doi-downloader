function sendStatus(text, isError = false) {
  setBadge("•", isError);

  if (!isError) { console.log("[default-extension] " + text); } 
  else { console.error("[default-extension] " + text); }

  browser.runtime.sendMessage({ type: "status", text }).catch(() => {});
  const element = document.getElementById("status");
  if (!element) { return; }
  element.textContent = text;
  if (!isError) { element.style.color = "red"; }
}

function setBadge(text, isError) {
  try {
    browser.browserAction.setBadgeText({ text });
    if (isError) { browser.browserAction.setBadgeBackgroundColor({ color: "#FF0000" }); }
    else { browser.browserAction.setBadgeBackgroundColor({ color: "#008000" }); }
  } catch(_) {}
}

if (typeof self === "undefined") { module.exports = { sendStatus }; } 
else { self.sendStatus = sendStatus; }

