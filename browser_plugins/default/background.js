const IGNORE_WEBREQUEST_ERRORS = new Set([
  "NS_BINDING_ABORTED",
  "NS_ERROR_TRACKING_URI",
  "NS_ERROR_DOM_BAD_URI",
]);

let captureSession = null; // { tabId, doi, expectedUrl, sawPdf, timeoutId }

async function armCaptureAndNavigate(pdfUrl, doi, tabId) {
  captureSession = {
    tabId,
    doi,
    expectedUrl: pdfUrl,
    sawPdf: false,
    timeoutId: null,
    pageCounter: 0,

    // debug/classification fields
    lastMainUrl: null,
    lastMainStatus: null,
    lastMainContentType: null,
  };

  captureSession.timeoutId = setTimeout(() => {
    if (! captureSession) return;

    const sc = captureSession.lastMainStatus || "";
    const ct = captureSession.lastMainContentType || "";
    const url = captureSession.lastMainUrl || captureSession.expectedUrl || "";

    if (sc === 401 || sc === 403) {
      self.failCapture(`Access denied (${sc}) — likely paywall/login required.`);
      captureSession = null;
    } else if (ct.includes("text/html") && self.looksPaywalledUrl(url)) {
      self.failCapture("Redirected to a paywall/purchase/login page (no PDF served).");
      captureSession = null;
    } else if (ct.includes("text/html")) {
      self.failCapture("Received HTML instead of PDF (likely paywall/login).");
      captureSession = null;
    } else {
      self.failCapture("No PDF response detected (possible paywall/login or blocked access).");
      captureSession = null;
    }
  }, CAPTURE_TIMEOUT_MS);

  captureSession.pageCounter++;
  if (captureSession.pageCounter <= 1 && !pdfUrl.toLowerCase().includes("download") && !pdfUrl.toLowerCase().includes("pdf")) {
    self.sendStatus("Armed capture; navigating to HTML…");
  } else {
    self.sendStatus("Armed capture; navigating to PDF…");
  }
  return browser.tabs.update(tabId, { url: pdfUrl });
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
    const sc = captureSession.lastMainStatus || "";
    const ct = captureSession.lastMainContentType || "";
    const url = captureSession.lastMainUrl || "";

    if (sc === 401 || sc === 403) {
      self.failCapture(`Access denied (${sc}) — likely paywall/login required.`);
      captureSession = null;
    } else if (ct.includes("text/html")) {
      self.failCapture("Received HTML instead of PDF after clicking (likely paywall/login).");
      captureSession = null;
    } else {
      self.failCapture("No PDF response detected after clicking the PDF button.");
      captureSession = null;
    }
  }, CAPTURE_TIMEOUT_MS);

  captureSession.pageCounter++;
  if (captureSession.pageCounter <= 1 && !pdfUrl.toLowerCase().includes("download") && !pdfUrl.toLowerCase().includes("pdf")) {
    self.sendStatus("Armed capture; navigating to HTML…");
  } else {
    self.sendStatus("Armed capture; navigating to PDF…");
  }
  return Promise.resolve(true);
}

function getHeader(headers, name) {
  name = name.toLowerCase();
  const h = (headers || []).find(x => x.name && x.name.toLowerCase() === name);
  return h ? h.value : null;
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

    self.sendStatus("PDF response detected; capturing…");

    const filter = browser.webRequest.filterResponseData(details.requestId);
    const chunks = [];

    filter.ondata = (e) => {
      filter.write(e.data);
      chunks.push(e.data);
    };

    const session = captureSession;
    filter.onstop = async () => {
      try {
        filter.disconnect();
        if (! session.expectBrowserDownload) {
          const blob = new Blob(chunks, { type: "application/pdf" });
          const objUrl = URL.createObjectURL(blob);
          const filename = `${self.sanitizeDOI(session.doi)}.pdf`;
          await browser.downloads.download({ url: objUrl, filename, saveAs: false });
          setTimeout(() => URL.revokeObjectURL(objUrl), 30000);
        }
      } catch (e) {
        self.failCapture(`Save failed: ${e.message}`);
        captureSession = null;
      } finally {
        captureSession = null;
      }
    };

    if (ct.includes("application/pdf")) {
      captureSession.expectBrowserDownload = true;
      sendStatus(`Server forces PDF download; will use browser download (avoid duplicate).`);
    }
  },
  { urls: ["<all_urls>"] },
  ["blocking", "responseHeaders"]
);

browser.webRequest.onCompleted.addListener(
  (details) => {
    if (!captureSession || details.tabId !== captureSession.tabId) return;

    if (details.type !== "main_frame") return;

    // If the main request completed but we never saw a PDF, report based on status.
    const ct = details.lastMainContentType || ""
    if (!captureSession.sawPdf) {
      if (!ct.includes("application/pdf")) return;
      if (captureSession.timeoutId) clearTimeout(captureSession.timeoutId);

      const sc = details.statusCode;
      if (sc === 401 || sc === 403) {
        self.failCapture(`Access denied (${sc}). You likely don’t have permission or need to sign in via your institution.`);
         captureSession = null;
      } else if (sc === 404) {
        self.failCapture("PDF not found (404). The link may be broken or moved.");
        captureSession = null;
      } else if (sc >= 400) {
        self.failCapture(`Server returned HTTP ${sc} (not a PDF).`);
        captureSession = null;
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
      self.failCapture(`Network error while loading PDF: ${details.error}`);
      captureSession = null;
    }
  },
  { urls: ["<all_urls>"] }
);

browser.runtime.onMessage.addListener((msg, sender) => {
  if (!msg || !msg.type) return;

  if (msg.type === "start-job") {
    return self.startJob(msg.url, msg.phrase, msg.doi);
  }

  if (msg.type === "save-log") {
    return self.saveLog();
  }

  if (msg.type === "who-am-i") {
    const tabId = sender && sender.tab ? sender.tab.id : null;
    return Promise.resolve({ tabId });
  }

  if (msg.type === "open-url" && msg.url) {
    self.sendStatus("Opening link in new tab…");
    return browser.tabs.create({ url: msg.url });
  }

  if (msg.type === "download_pdf_via_tab_capture" && msg.pdfUrl) {
    const tabId = msg.tabId || (sender && sender.tab ? sender.tab.id : null);
    const doi = msg.doi || null;

    if (!tabId) {
      self.sendStatus("Cannot download: missing tabId.");
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
    self.sendStatus(`✅ Saved PDF to ${item.filename}`);
  });
});
