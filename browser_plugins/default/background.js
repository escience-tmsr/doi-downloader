browser.webRequest.onHeadersReceived.addListener(
  (details) => {
    if (!self.inRetrievePdfSession(details.tabId)) return;
    self.storeDetailsInSessionData(details);

    if (!self.retrievingPdfFile(details)) return;

    captureSession.sawPdf = true;
    clearTimeout(captureSession.timeoutId);
    self.sendStatus("PDF response detected; capturing…");

    if (retrievingAttachment(details)) {
      captureSession.expectBrowserDownload = true;
      sendStatus(`Server forces PDF download; will use browser download to avoid duplicate (${captureSession.pageCounter})`);
    };

    self.processIncomingPdfData(details);
  },
  { urls: ["<all_urls>"] },
  ["blocking", "responseHeaders"]
);

browser.webRequest.onCompleted.addListener(
  (details) => {
    if (self.inRetrievePdfSession(details.tabId) &&
        self.retrievingPdfFile(details) &&
        !captureSession.sawPdf) {
      clearTimeout(captureSession.timeoutId);
      switch (details.statusCode) {
        case 401:
        case 403: 
          self.failCapture(`Access denied (${sc}). You likely don’t have permission or need to sign in via your institution.`);
          captureSession = null;
          break;
        case 404:
          self.failCapture("PDF not found (404). The link may be broken or moved.");
          captureSession = null;
          break
        default:
          if (details.statusCode >= 400) {
            self.failCapture(`Server returned HTTP ${details.statusCode} (not a PDF).`);
            captureSession = null;
          }
      } 
    }
  },
  { urls: ["<all_urls>"] }
);

browser.webRequest.onErrorOccurred.addListener(
  (details) => {
    if (!self.inRetrievePdfSession(details.tabId)) return;

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
  if (!msg || !msg.type || msg.type === "status") return;

  if (msg.type !== "what-is-my-tabid") {
    sendStatus(`entering onMessage: ${msg.type}`);
  } else {
    const tabId = sender && sender.tab ? sender.tab.id : null;
    return Promise.resolve({ tabId });
  }

  if (msg.type === "start-job") return self.startJob(msg.doi);

  if (msg.type === "save-log") return self.saveLog(downloadLog);

  if (msg.type === "arm_capture_for_tab") return armCaptureOnly(msg.doi, msg.tabId, msg.expectedUrl ?? null);

  if (msg.type === "open-url" && msg.url) {
    self.sendStatus("Opening link in new tab…");
    return browser.tabs.create({ url: msg.url });
  }

  if (msg.type === "download_pdf_via_tab_capture" && msg.pdfUrl) {
    const tabId = msg.tabId || (sender && sender.tab ? sender.tab.id : null);
    const doi = msg.doi || null;

    if (!tabId) {
      self.sendStatus("Cannot download: missing tabId.", isError = false);
      return;
    }
    return armCaptureAndNavigate(doi, tabId, msg.pdfUrl);
  }

  self.sendStatus(`onMessage: cannot process message: ${msg.type}`, isError = false);
});

browser.downloads.onChanged.addListener((delta) => {
  if (!delta.state || delta.state.current !== "complete") return;

  browser.downloads.search({ id: delta.id }).then(([item]) => {
    if (!item) return;
    if (captureSession !== null) {
      self.sendStatus(`✅ Saved PDF to ${item.filename}`);
      downloadLog = downloadLog.concat(captureSession.doi, ",", item.filename, "\n");
    }
  });
});
