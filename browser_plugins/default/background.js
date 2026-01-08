// Background script
// - Starts a "job" by opening the DOI URL in a new tab and storing job metadata.
// - Content script finds a PDF link/button and asks the background to capture-and-save the PDF.
// - We cannot click Firefox's PDF viewer download button (browser UI), so we capture the PDF bytes
//   from the network response stream (Firefox-only: webRequest.filterResponseData) while the PDF loads
//   in a normal tab context (with cookies/referrer/session), then save to Downloads/papers/.

const CAPTURE_TIMEOUT_MS = 15000;

let captureSession = null; // { tabId, doi, startedAt, timeoutId }

// ----- helpers -----

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

function headerValue(headers, name) {
  const n = name.toLowerCase();
  const h = (headers || []).find(x => (x.name || "").toLowerCase() === n);
  return h && h.value ? h.value : "";
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

// ----- job start -----

function startJob(url, phrase, doi) {
  const normalizedDoi = doi || extractDoiFromUrl(url) || null;

  return browser.tabs.create({ url }).then(tab => {
    const job = {
      url,
      phrase,
      doi: normalizedDoi,
      used: false,
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

// ----- PDF capture & save -----

async function armCaptureAndNavigate(tabId, pdfUrl, doi) {
  if (captureSession && captureSession.timeoutId) {
    clearTimeout(captureSession.timeoutId);
  }

  captureSession = {
    tabId,
    doi,
    startedAt: Date.now(),
    timeoutId: null
  };

  captureSession.timeoutId = setTimeout(() => {
    if (captureSession && captureSession.tabId === tabId) {
      sendStatus("Timed out waiting for PDF response.");
      captureSession = null;
    }
  }, 30000);

  sendStatus("Armed capture; navigating to PDF…");
  await browser.tabs.update(tabId, { url: pdfUrl });
}

browser.webRequest.onHeadersReceived.addListener(
  (details) => {
    if (!captureSession || details.tabId !== captureSession.tabId) return;

    const ct = headerValue(details.responseHeaders, "content-type").toLowerCase();
    const cd = headerValue(details.responseHeaders, "content-disposition").toLowerCase();

    const looksLikePdf =
      ct.includes("application/pdf") ||
      /\.pdf([?#].*)?$/i.test(details.url) ||
      cd.includes(".pdf");

    if (!looksLikePdf) return;

    const { doi } = captureSession;
    if (captureSession.timeoutId) clearTimeout(captureSession.timeoutId);
    captureSession = null; // avoid double capture

    sendStatus("PDF response detected; capturing bytes…");

    const filter = browser.webRequest.filterResponseData(details.requestId);
    const chunks = [];

    filter.ondata = (event) => {
      filter.write(event.data);     // keep viewer working
      chunks.push(event.data);      // capture bytes
    };

    filter.onstop = async () => {
      try {
        filter.disconnect();

        const blob = new Blob(chunks, { type: "application/pdf" });
        const objUrl = URL.createObjectURL(blob);

        const filename = `${safeFilenameFromDoi(doi)}.pdf`;

        await browser.downloads.download({
          url: objUrl,
          filename,
          saveAs: false
        });

        sendStatus(`Saved PDF to Downloads/${filename}`);
        setTimeout(() => URL.revokeObjectURL(objUrl), 60000);
      } catch (e) {
        sendStatus(`Capture/save failed: ${e && e.message ? e.message : e}`);
      }
    };
  },
  { urls: ["<all_urls>"] },
  ["blocking", "responseHeaders"]
);

// ----- message routing -----

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
    return armCaptureAndNavigate(tabId, msg.pdfUrl, doi);
  }
});

browser.webRequest.onCompleted.addListener(
  (details) => {
    if (!captureSession || details.tabId !== captureSession.tabId) return;

    // If the main request completed but we never saw a PDF, report based on status.
    if (!captureSession.sawPdf) {
      if (captureSession.timeoutId) clearTimeout(captureSession.timeoutId);

      const sc = details.statusCode;
      if (sc === 401 || sc === 403) {
        failCapture(`Access denied (${sc}). You likely don’t have permission or need to sign in via your institution.`);
      } else if (sc === 404) {
        failCapture("PDF not found (404). The link may be broken or moved.");
      } else if (sc >= 400) {
        failCapture(`Server returned HTTP ${sc} (not a PDF).`);
      } else {
        // 200 but not a PDF: often an HTML landing/login page
        failCapture("Received a non-PDF response (often a login/landing page).");
      }
    }
  },
  { urls: ["<all_urls>"] }
);

browser.webRequest.onErrorOccurred.addListener(
  (details) => {
    if (!captureSession || details.tabId !== captureSession.tabId) return;

    if (captureSession.timeoutId) clearTimeout(captureSession.timeoutId);
    failCapture(`Network error: ${details.error}`);
  },
  { urls: ["<all_urls>"] }
);

function failCapture(reason) {
  if (!captureSession) return;
  sendStatus(`❌ PDF download failed: ${reason}`);
  captureSession = null;
}

async function openPdfAndCapture(pdfUrl, doi, tabId) {
  // Arm capture first
  captureSession = {
    tabId,
    doi,
    expectedUrl: pdfUrl,
    sawPdf: false,
    timeoutId: null,
    lastStatusCode: null,
  };

  // Watchdog: if no PDF arrives
  captureSession.timeoutId = setTimeout(() => {
    // If we never saw a PDF response, give a helpful message
    failCapture("No PDF response detected (possible no access rights, login required, or blocked download).");
  }, CAPTURE_TIMEOUT_MS);

  sendStatus("Armed capture; navigating to PDF…");
  await browser.tabs.update(tabId, { url: pdfUrl });
}

