const { findElementByPhrase, performAction, sendStatus }  = require("../src/content.functions");

test("sendStatus", () => {
  global.browser = {"runtime": {"sendMessage": jest.fn()}};
  global.console = {"log": jest.fn()};
  const text = "text";
  sendStatus(text);
  expect(self.browser.runtime.sendMessage).toHaveBeenCalledTimes(1);
  expect(self.console.log).toHaveBeenCalledTimes(1);
});

test("findElementByPhrase", () => {
  let data = document.createElement("a");
  data.title = "innerText.outerText";
  document.querySelectorAll = jest.fn().mockReturnValue([data]);
  let phrases = ["abc", "def"];
  self.sendStatus = jest.fn();
  let result = findElementByPhrase(phrases);
  expect(result).toBe(null);
  expect(document.querySelectorAll).toHaveBeenCalledTimes(phrases.length);
  expect(self.sendStatus).toHaveBeenCalledTimes(phrases.length * 2);

  self.sendStatus.mockClear();
  phrases = ["innerText", "outerText"];
  result = findElementByPhrase(phrases);
  expect(self.sendStatus).toHaveBeenCalledTimes(2);
  expect(result).not.toBe(null);
});

test("performAction", async() => {
  const job = {"phrase": "abc"}
  const myTabId = 0;
  self.findElementByPhrase = jest.fn().mockReturnValue([]);
  self.sendStatus.mockClear();
  let result = await performAction(job, myTabId);
  expect(result).toBe("not found");
  expect(self.sendStatus).toHaveBeenCalledTimes(8);

  let data = document.createElement("a");
  data.title = "innerText.outerText";
  data.tagName = {"toLowerCase": jest.fn(),};
  data.href = "href";
  self.findElementByPhrase = jest.fn().mockReturnValue([data]);
  result = await performAction(job, myTabId);
  expect(result).toBe("not found");
  expect(self.sendStatus).toHaveBeenCalledTimes(2);
});

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
