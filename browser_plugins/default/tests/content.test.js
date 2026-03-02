const { findElementByPhrase, performAction, sendStatus }  = require("../src/content.functions");

test("sendStatus", () => {
  global.browser = {"runtime": {"sendMessage": jest.fn()}};
  global.console = {"log": jest.fn()};
  const text = "text";
  sendStatus(text);
  expect(self.browser.runtime.sendMessage).toHaveBeenCalledTimes(1);
  expect(self.console.log).toHaveBeenCalledTimes(1);
});


// function sendStatus(text) {
//   try { browser.runtime.sendMessage({ type: "status", text }); } catch (_) {}
//   console.log("[default-extension]", text);
// }
// 
// function findElementByPhrase(phrases) {
//   for (const phrase of phrases) {
//     const needle = phrase.toLowerCase();
//     sendStatus(`[default-extension] searching for phrase: ${needle}`);
//   
//     const elements = Array.from(document.querySelectorAll("a, button"));
//     for (const el of elements) {
//       const text  = (el.innerText || el.textContent || "").trim();
//       const aria  = el.getAttribute("aria-label") || "";
//       const title = el.getAttribute("title") || "";
//   
//       const combined = (text + " " + aria + " " + title).toLowerCase();
//   
//       if (combined.includes(needle)) {
//         sendStatus(`[default-extension] found key "${needle}", tag: ${el.tagName}, target: ${el.href}`);
//         return el;
//       }
//     }
//   
//     sendStatus(`[default-extension] no element found for phrase: ${phrase}`);
//   }
//   return null;
// }
// 
// async function performAction(job, myTabId) {
//   sendStatus("Entering performAction...")
//   const phrase = job.phrase;
//   const el = findElementByPhrase(phrase);
// 
//   if (!el) {
//     sendStatus(`❌ No link or button found containing "${phrase}"`);
//     return;
//   }
// 
//   const tag = el.tagName.toLowerCase();
// 
//   if (tag === "a" && el.href) {
//     const pdfUrl = el.href;
//     sendStatus(`Found candidate link for "${phrase}", processing…`);
// 
//     browser.runtime.sendMessage({
//       type: "download_pdf_via_tab_capture",
//       pdfUrl,
//       doi: job.doi || null,
//       tabId: myTabId
//     }).catch(err => {
//       sendStatus(`Error asking add-on to capture PDF: ${err}`);
//     });
// 
//     return;
//   }
// 
//   sendStatus("Arming capture…");
// 
//   await browser.runtime.sendMessage({
//     type: "arm_capture_for_tab",
//     doi: job.doi,
//     tabId: myTabId
//   });
// 
//   sendStatus(`Clicking "${phrase}" button…`);
//   try {
//     el.click();
//   } catch (e) {
//     sendStatus(`Failed clicking element: ${e.message}`);
//   }
// }
// 
// async function maybeRunJob(myTabId) {
//   const result = await browser.storage.local.get("job").catch(err => {
//     sendStatus(`[default-extension] error reading job from storage: ${err}`);
//   });
//   const job = result.job;
//   if (!job || job.tabId !== myTabId) return;
//   sendStatus(`Entered maybeRunJob, tabId is ${myTabId}, url is ${job.url}`);
// 
//   const here = location.href;
//   if (job.used && job.usedUrl.includes(here)) {
//     sendStatus(`Skipping: already processed this page.`);
//     return;
//   }
// 
//   job.used = true;
//   job.usedUrl.push(here);
//   await browser.storage.local.set({ job });
// 
//   sendStatus("[default-extension] tabId matches job, running job");
//   browser.storage.local.set({ job }).catch(err => {
//     sendStatus(`[default-extension] error marking job used: ${err}`);
//   });
// 
//   window.setTimeout(() => {
//     try {
//       performAction(job, myTabId);
//     } catch (e) {
//       sendStatus(`Error while searching link: ${e.message}`);
//     }
//   }, 1000);
// }
