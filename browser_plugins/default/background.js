const CAPTURE_TIMEOUT_MS = 15000;

const IGNORE_WEBREQUEST_ERRORS = new Set([
  "NS_BINDING_ABORTED",
  "NS_ERROR_TRACKING_URI",
  "NS_ERROR_DOM_BAD_URI",
]);

let captureSession = null; // { tabId, doi, expectedUrl, sawPdf, timeoutId }

function extractDoiFromUrl(url) {
  if (!url) return null;
  const m = String(url).match(/doi\.org\/(.+)$/i);
  return m ? decodeURIComponent(m[1]) : null;
}

function sanitizeForFilename(input) {
  return (input || "paper")
    .trim()
    .replace(/^https?:\/\//i, "")
    .replace(/[^a-z0-9._-]+/gi, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 150);
}

function safeFilenameFromDoi(doi) {
  return sanitizeForFilename((doi || "paper").replace(/^doi:/i, ""));
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

function armCaptureAndNavigate(pdfUrl, doi, tabId) {
  captureSession = {
    tabId,
    doi,
    expectedUrl: pdfUrl,
    sawPdf: false,
    timeoutId: null,

    // debug/classification fields
    lastMainUrl: null,
    lastMainStatus: null,
    lastMainContentType: null,
  };

  captureSession.timeoutId = setTimeout(() => {
    const sc = captureSession.lastMainStatus;
    const ct = captureSession.lastMainContentType || "";
    const url = captureSession.lastMainUrl || captureSession.expectedUrl || "";

    // One final, user-friendly message:
    if (sc === 401 || sc === 403) {
      failCapture(`Access denied (${sc}) — likely paywall/login required.`);
    } else if (ct.includes("text/html") && looksPaywalledUrl(url)) {
      failCapture("Redirected to a paywall/purchase/login page (no PDF served).");
    } else if (ct.includes("text/html")) {
      failCapture("Received HTML instead of PDF (likely paywall/login).");
    } else {
      failCapture("No PDF response detected (possible paywall/login or blocked access).");
    }
  }, CAPTURE_TIMEOUT_MS);

  sendStatus("Armed capture; navigating to PDF…");
  return browser.tabs.update(tabId, { url: pdfUrl });
}

function failCapture(reason) {
  if (!captureSession) return;
  sendStatus(`❌ PDF download failed: ${reason}`);
  captureSession = null;
}

function looksPaywalledUrl(u) {
  return ["paywall","subscribe","purchase","checkout","cart","basket","login","signin","account"]
    .some(k => u.includes(k));
}

function armCaptureOnly(doi, tabId, expectedUrl = null) {
  captureSession = {
    tabId,
    doi,
    expectedUrl,
    sawPdf: false,
    timeoutId: null,
    lastMainUrl: null,
    lastMainStatus: null,
    lastMainContentType: null,
  };

  captureSession.timeoutId = setTimeout(() => {
    const sc = captureSession.lastMainStatus;
    const ct = captureSession.lastMainContentType || "";
    const url = captureSession.lastMainUrl || "";

    if (sc === 401 || sc === 403) {
      failCapture(`Access denied (${sc}) — likely paywall/login required.`);
    } else if (ct.includes("text/html")) {
      failCapture("Received HTML instead of PDF after clicking (likely paywall/login).");
    } else {
      failCapture("No PDF response detected after clicking the PDF button.");
    }
  }, CAPTURE_TIMEOUT_MS);

  sendStatus("Armed capture; you can click the PDF button now…");
  return Promise.resolve(true);
}

///////////////////////////////////////////////////////////////////////////////////////////////////////

browser.webRequest.onHeadersReceived.addListener(
  (details) => {
    if (!captureSession || details.tabId !== captureSession.tabId) return;

    const headers = details.responseHeaders || [];
    const ct = (headers.find(h => h.name.toLowerCase() === "content-type")?.value || "").toLowerCase();

    // Always record main navigation info for paywall classification
    if (details.type === "main_frame") {
      captureSession.lastMainUrl = details.url;
      captureSession.lastMainStatus = details.statusCode;
      captureSession.lastMainContentType = ct;
    }

    // ✅ Only confirm PDF by content-type
    if (!ct.includes("application/pdf")) {
      return; // DO NOT clear timeout here
    }

    // Confirmed PDF
    captureSession.sawPdf = true;
    if (captureSession.timeoutId) clearTimeout(captureSession.timeoutId);

    sendStatus("PDF response detected; capturing…");

    const filter = browser.webRequest.filterResponseData(details.requestId);
    const chunks = [];

    filter.ondata = (e) => {
      filter.write(e.data);
      chunks.push(e.data);
    };

    filter.onstop = async () => {
      try {
        filter.disconnect();
        const blob = new Blob(chunks, { type: "application/pdf" });
        const objUrl = URL.createObjectURL(blob);

        const filename = `${safeFilenameFromDoi(captureSession.doi)}.pdf`;
        await browser.downloads.download({ url: objUrl, filename, saveAs: false });

        //sendStatus(`✅ Saved PDF to Downloads/${filename}`);
        setTimeout(() => URL.revokeObjectURL(objUrl), 60_000);
      } catch (e) {
        failCapture(`Save failed: ${e.message}`);
      } finally {
        captureSession = null;
      }
    };
  },
  { urls: ["<all_urls>"] },
  ["blocking", "responseHeaders"]
);

browser.webRequest.onCompleted.addListener(
  (details) => {
    if (!captureSession || details.tabId !== captureSession.tabId) return;

    if (details.type !== "main_frame") return;

    // If the main request completed but we never saw a PDF, report based on status.
    if (!captureSession.sawPdf) {
      if (!ct.includes("application/pdf")) return;
      if (captureSession.timeoutId) clearTimeout(captureSession.timeoutId);

      const sc = details.statusCode;
      if (sc === 401 || sc === 403) {
        failCapture(`Access denied (${sc}). You likely don’t have permission or need to sign in via your institution.`);
      } else if (sc === 404) {
        failCapture("PDF not found (404). The link may be broken or moved.");
      } else if (sc >= 400) {
        failCapture(`Server returned HTTP ${sc} (not a PDF).`);
      } 
    }
  },
  { urls: ["<all_urls>"] }
);

browser.webRequest.onErrorOccurred.addListener(
  (details) => {
    if (!captureSession || details.tabId !== captureSession.tabId) return;

    // Ignore common non-fatal / policy / handoff errors
    if (IGNORE_WEBREQUEST_ERRORS.has(details.error)) {
      console.log("[capture] ignoring", details.error, "for", details.type, details.url);
      return;
    }

    // Most errors here are subresources; don't kill the session.
    // Record for better timeout messages, but let the watchdog decide.
    captureSession.lastError = details.error;
    captureSession.lastErrorUrl = details.url;

    console.log("[capture] webRequest error (non-fatal):", details.error, details.type, details.url);

    // OPTIONAL: Only fail fast if it's clearly the main navigation to the expected PDF URL
    // and we haven't seen a PDF.
    const urlMatchesExpected =
      captureSession.expectedUrl &&
      (details.url === captureSession.expectedUrl ||
       details.url.startsWith(captureSession.expectedUrl));

    if (!captureSession.sawPdf && details.type === "main_frame" && urlMatchesExpected) {
      if (!ct.includes("application/pdf")) return;
      if (captureSession.timeoutId) clearTimeout(captureSession.timeoutId);
      failCapture(`Network error while loading PDF: ${details.error}`);
    }
  },
  { urls: ["<all_urls>"] }
);

browser.runtime.onMessage.addListener((msg, sender) => {
  if (!msg || !msg.type) return;

  if (msg.type === "start-job") {
    return startJob(msg.url, msg.phrase, msg.doi);
  }

  if (msg.type === "who-am-i") {
    const tabId = sender && sender.tab ? sender.tab.id : null;
    return Promise.resolve({ tabId });
  }

  if (msg.type === "open-url" && msg.url) {
    sendStatus("Opening link in new tab…");
    return browser.tabs.create({ url: msg.url });
  }

  if (msg.type === "download_pdf_via_tab_capture" && msg.pdfUrl) {
    const tabId = msg.tabId || (sender && sender.tab ? sender.tab.id : null);
    const doi = msg.doi || null;

    if (!tabId) {
      sendStatus("Cannot download: missing tabId.");
      return;
    }
    return armCaptureAndNavigate(msg.pdfUrl, doi, tabId);
  }

  if (msg.type === "arm_capture_for_tab") {
    return armCaptureOnly(msg.doi, msg.tabId, msg.expectedUrl ?? null);
  }
});

browser.downloads.onChanged.addListener((delta) => {
  if (!delta.state || delta.state.current !== "complete") return;

  browser.downloads.search({ id: delta.id }).then(([item]) => {
    if (!item) return;
    sendStatus(`✅ Saved PDF to ${item.filename}`);
  });
});
