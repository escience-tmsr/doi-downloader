console.log("[default-plugin] content-script injected on", window.location.href);

function findElementByPhrase(phrase) {
  const needle = phrase.toLowerCase();
  console.log("[default-plugin] searching for phrase:", needle);

  // Search <a> and <button> elements
  const elements = Array.from(document.querySelectorAll("a, button"));

  for (const el of elements) {
    const text  = (el.innerText || el.textContent || "").trim();
    const aria  = el.getAttribute("aria-label") || "";
    const title = el.getAttribute("title") || "";

    const combined = (text + " " + aria + " " + title).toLowerCase();

    if (combined.includes(needle)) {
      console.log("[default-plugin] matched element:", combined, "tag:", el.tagName);
      return el;
    }
  }

  console.log("[default-plugin] no element found for phrase:", phrase);
  return null;
}

function performAction(phrase) {
  const el = findElementByPhrase(phrase);
  if (!el) {
    alert(`No link or button found containing:\n\n"${phrase}"`);
    return;
  }

  const tag = el.tagName.toLowerCase();

  // If it's a link with an href, ask background.js to open it in a new tab
  if (tag === "a" && el.href) {
    const targetUrl = el.href;
    console.log("[default-plugin] found link href:", targetUrl);

    browser.runtime.sendMessage({
      type: "open-url",
      url: targetUrl
    }).catch(err => {
      console.error("[default-plugin] error sending open-url:", err);
      alert("Error asking add-on to open URL: " + err);
    });

    return;
  }

  // Otherwise, click the element (for JS-driven buttons)
  console.log("[default-plugin] clicking non-link element:", el);
  el.click();
  alert(`Clicked element containing:\n\n"${phrase}"`);
}

function maybeRunJob(myTabId) {
  browser.storage.local.get("job").then(result => {
    const job = result.job;
    if (!job) {
      console.log("[default-plugin] no job in storage, doing nothing");
      return;
    }

    if (job.tabId !== myTabId) {
      console.log("[default-plugin] tabId mismatch (mine:", myTabId, "job:", job.tabId, "), skipping");
      return;
    }

    console.log("[default-plugin] tabId matches job, running job");

    // Mark job as used so other tabs won't run it
    job.used = true;
    browser.storage.local.set({ job }).catch(err => {
      console.error("[default-plugin] error marking job used:", err);
    });

    // Wait a bit for dynamic content, then perform the action
    window.setTimeout(() => {
      try {
        performAction(job.phrase);
      } catch (e) {
        console.error("[default-plugin] error in performAction:", e);
        alert("Error while searching link: " + e.message);
      }
    }, 1000); // 1 second delay
  }).catch(err => {
    console.error("[default-plugin] error reading job from storage:", err);
  });
}

// Ask background who we are (our tabId), then maybe run the job
browser.runtime.sendMessage({ type: "who-am-i" })
  .then(response => {
    const myTabId = response && response.tabId;
    console.log("[default-plugin] my tabId is", myTabId);
    if (myTabId != null) {
      // Run logic a bit after injection
      window.setTimeout(() => maybeRunJob(myTabId), 500);
    } else {
      console.log("[default-plugin] no tabId available, doing nothing");
    }
  })
  .catch(err => {
    console.error("[default-plugin] error getting tabId:", err);
  });
