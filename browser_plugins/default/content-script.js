console.log("[default-extension] content-script injected on", window.location.href);

function sendStatus(text) {
  try { browser.runtime.sendMessage({ type: "status", text }); } catch (_) {}
  console.log("[default-extension]", text);
}

function findElementByPhrase(phrase) {
  const needle = phrase.toLowerCase();
  console.log("[default-extension] searching for phrase:", needle);

  const elements = Array.from(document.querySelectorAll("a, button"));
  for (const el of elements) {
    const text  = (el.innerText || el.textContent || "").trim();
    const aria  = el.getAttribute("aria-label") || "";
    const title = el.getAttribute("title") || "";

    const combined = (text + " " + aria + " " + title).toLowerCase();

    if (combined.includes(needle)) {
      console.log("[default-extension] matched element:", combined, "tag:", el.tagName);
      return el;
    }
  }

  console.log("[default-extension] no element found for phrase:", phrase);
  return null;
}

async function performAction(job, myTabId) {
  sendStatus("Entering performAction...")
  const phrase = job.phrase;
  const el = findElementByPhrase(phrase);

  if (!el) {
    sendStatus(`❌ No link or button found containing "${phrase}"`);
    return;
  }

  const tag = el.tagName.toLowerCase();

  if (tag === "a" && el.href) {
    const pdfUrl = el.href;
    sendStatus(`Found candidate link for "${phrase}", processing…`);

    browser.runtime.sendMessage({
      type: "download_pdf_via_tab_capture",
      pdfUrl,
      doi: job.doi || null,
      tabId: myTabId
    }).catch(err => {
      sendStatus("Error asking add-on to capture PDF: " + err);
    });

    return;
  }

  sendStatus("Arming capture…");

  await browser.runtime.sendMessage({
    type: "arm_capture_for_tab",
    doi: job.doi,
    tabId: myTabId
  });

  sendStatus(`Clicking "${phrase}" button…`);
  try {
    el.click();
  } catch (e) {
    sendStatus(`Failed clicking element: ${e.message}`);
  }
}

async function maybeRunJob(myTabId) {
  console.log("Entering maybeRunJob");
  const result = await browser.storage.local.get("job").catch(err => {
    console.error("[default-extension] error reading job from storage:", err);
  });
  const job = result.job;
  if (!job) {
    console.log("[default-extension] no job in storage, doing nothing");
    return;
  }

  if (job.tabId !== myTabId) {
    console.log("[default-extension] tabId mismatch (mine:", myTabId, "job:", job.tabId, "), skipping");
    return;
  }

  const here = location.href;
  if (job.used && job.usedUrl === here) {
    sendStatus(`Skipping: already processed this page.`);
    return;
  }

  job.used = true;
  job.usedUrl = here;
  console.log(`maybeRunJob: ${job.used} # ${job.usedUrl} # ${job.tabId}`)
  await browser.storage.local.set({ job });

  console.log("[default-extension] tabId matches job, running job");
  job.used = true;
  browser.storage.local.set({ job }).catch(err => {
    console.error("[default-extension] error marking job used:", err);
  });

  window.setTimeout(() => {
    try {
      performAction(job, myTabId);
    } catch (e) {
      sendStatus("Error while searching link: " + e.message);
    }
  }, 1000);
}

browser.runtime.sendMessage({ type: "who-am-i" })
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
