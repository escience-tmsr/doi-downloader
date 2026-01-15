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

function extractDoiFromUrl(url) {
  if (!url) return null;
  const m = String(url).match(/doi\.org\/(.+)$/i);
  return m ? decodeURIComponent(m[1]) : null;
}

function setBadge(text) {
  try { browser.browserAction.setBadgeText({ text }); } catch (_) {}
}

function sendStatus(text) {
  console.log("[default-extension]", text);
  setBadge("•");
  try { browser.runtime.sendMessage({ type: "status", text }); } catch (_) {}
  try {
    browser.notifications.create({
      type: "basic",
      title: "PDF helper",
      message: text
    });
  } catch (_) {}
}

function startJob(url, phrase, doi) {
  const normalizedDoi = doi || extractDoiFromUrl(url) || null;

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
    console.error("[default-extension] error in startJob:", err);
    sendStatus(`Could not start job: ${err && err.message ? err.message : err}`);
    throw err;
  });
}

function looksPaywalledUrl(u) {
  return ["paywall","subscribe","purchase","checkout","cart","basket","login","signin","account"]
    .some(k => u.includes(k));
}

function failCapture(reason, captureSession) {
  if (!captureSession) return;
  self.sendStatus(`❌ PDF download failed: ${reason}`);
  captureSession = null;
  return captureSession;
}

if (typeof self === "undefined") {
  module.exports = { sanitizeDOI, sendStatus, startJob };
} else {
  self.failCapture = failCapture
  self.looksPaywalledUrl = looksPaywalledUrl;
  self.sanitizeDOI = sanitizeDOI;
  self.sendStatus = sendStatus;
  self.startJob = startJob;
}