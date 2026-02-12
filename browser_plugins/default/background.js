browser.webRequest.onHeadersReceived.addListener(
  (details) => {
    if (!captureSession || details.tabId !== captureSession.tabId) return;

    const headers = details.responseHeaders || [];
    const ct = (headers.find(h => h.name.toLowerCase() === "content-type")?.value || "").toLowerCase();
    const cd = (headers.find(h => h.name.toLowerCase() === "content-disposition")?.value || "").toLowerCase();

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
    sendStatus(`breakpoint 1: ${ct}`)

    // Confirmed PDF
    captureSession.sawPdf = true;
    if (captureSession.timeoutId) clearTimeout(captureSession.timeoutId);

    self.sendStatus("PDF response detected; capturing…");

    if (cd.includes("attachment")) {
      captureSession.expectBrowserDownload = true;
      sendStatus(`Server forces PDF download; will use browser download to avoid duplicate (${captureSession.pageCounter})`);
    };

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
          const filename = `${self.removeSlashes(self.sanitizeDOI(session.doi))}.pdf`;
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
  if (!msg || !msg.type || msg.type === "status") return;
  sendStatus(`entering onMessage: ${msg.type}`);

  if (msg.type === "start-job") {
    return self.startJob(msg.doi);
  }

  if (msg.type === "save-log") {
    return self.saveLog(sessionLog);
  }

  if (msg.type === "what-is-my-tabid") {
    const tabId = sender && sender.tab ? sender.tab.id : null;
    sendStatus(`answer: tabId=${tabId}`);
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
      self.sendStatus("Cannot download: missing tabId.", isError = false);
      return;
    }
    return armCaptureAndNavigate(doi, tabId, msg.pdfUrl);
  }

  if (msg.type === "arm_capture_for_tab") {
    return armCaptureOnly(msg.doi, msg.tabId, msg.expectedUrl ?? null);
  }

  self.sendStatus(`onMessage: cannot process message: ${msg.type}`, isError = false);
});

browser.downloads.onChanged.addListener((delta) => {
  if (!delta.state || delta.state.current !== "complete") return;

  browser.downloads.search({ id: delta.id }).then(([item]) => {
    if (!item) return;
    self.sendStatus(`✅ Saved PDF to ${item.filename}`);
    if (captureSession !== null) {
      sessionLog = sessionLog.concat(captureSession.doi, ",", item.filename, "\n");
    }
  });
});
