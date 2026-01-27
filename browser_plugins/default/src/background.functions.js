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
  try { browser.browserAction.setBadgeText({ text }); } catch(_) {}
}

function sendStatus(text) {
  //try { browser.runtime.sendMessage({ type: "status", text }); } catch (_) {}
  browser.runtime.sendMessage({ type: "status", text }).catch(() => {});
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

function saveLog() {
  const table = [{ name: "test1", property: 1},
                 { name: "test2", property: 2}]

  const csv = "test1,1\ntest2,2\n";
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);

  browser.downloads.download({
    url,
    filename: "my_table.csv",
    conflictAction: "uniquify"
  });
  sendStatus("Saved logfile to Downloads directory");
}

if (typeof self === "undefined") {
  module.exports = { failCapture, looksPaywalledUrl, sanitizeDOI, saveLog, sendStatus, startJob };
} else {
  self.failCapture = failCapture
  self.looksPaywalledUrl = looksPaywalledUrl;
  self.sanitizeDOI = sanitizeDOI;
  self.saveLog = saveLog;
  self.sendStatus = sendStatus;
  self.startJob = startJob;
}
