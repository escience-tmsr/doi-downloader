const CAPTURE_TIMEOUT_MS = 15000;

function sanitizeDOI(doi) {
  return doi
    .trim()
    .replace(/^doi:\s*/i, "")
    .replace(/^(https?:\/\/)?doi.org\//i, "")
    .replace(/[^a-z0-9._-]+/gi, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 100);
}

function setBadge(text) {
  try { browser.browserAction.setBadgeText({ text }); } catch (_) {}
}

function sendStatus(text) {
  try { browser.runtime.sendMessage({ type: "status", text }); } catch (_) {}
  console.log("[default-extension]", text);
  setBadge("•");
}

function startJob(url, phrase, doi) {
  const normalizedDoi = doi || sanitizeDOI(url) || null;

  return browser.tabs.create({ url }).then(tab => {
    const job = {
      url,
      phrase,
      doi: normalizedDoi,
      used: false,
      usedUrl: null,
      tabId: tab.id
    };

    sendStatus(`Opened DOI page in tab ${tab.id}. Looking for "${phrase}" link…`);
    return browser.storage.local.set({ job });
  }).catch(err => {
    sendStatus(`Could not start job: ${err && err.message ? err.message : err}`);
    throw err;
  });
}

function looksPaywalledUrl(u) {
  return ["paywall","subscribe","purchase","checkout","cart","basket","login","signin","account"]
    .some(k => u.includes(k));
}

function failCapture(reason, captureSession) {
  sendStatus(`❌ PDF download failed: ${reason}`);
  return
}

if (typeof self === "undefined") {
  module.exports = { failCapture, looksPaywalledUrl, sanitizeDOI, sendStatus, startJob };
} else {
  self.failCapture = failCapture
  self.looksPaywalledUrl = looksPaywalledUrl;
  self.sanitizeDOI = sanitizeDOI;
  self.sendStatus = sendStatus;
  self.startJob = startJob;
}