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
  let data = document.createElement("a");
  data.innerText = "outerText";
  data.href = "href";
  self.findElementByPhrase = jest.fn().mockReturnValue(data);
  global.browser = {"runtime": {"sendMessage": jest.fn().mockResolvedValue()}};
  self.sendStatus = jest.fn();
  let result = await performAction(job, myTabId);
  expect(self.sendStatus).toHaveBeenCalledTimes(2);
  expect(result).toBe("link found");

  data = document.createElement("button");
  self.findElementByPhrase = jest.fn().mockReturnValue(data);
  result = await performAction(job, myTabId);
  expect(result).toBe("button found");

  self.findElementByPhrase = jest.fn().mockReturnValue();
  result = await performAction(job, myTabId);
  expect(result).toBe("not found");
});

test("maybeRunJob", async() => {
  const myTabId = 67;
  let job = {
    "tabId": myTabId, 
    "used": true,
    "usedUrl": [],
  }          
  global.browser = {"storage": {"local": {
    "get": jest.fn().mockResolvedValue({"job": job}),
    "set": jest.fn().mockResolvedValue(),
  }}};
  global.locations = {"href": "here"};
  self.sendStatus = jest.fn();
  await maybeRunJob(myTabId);
  expect(self.sendStatus).toHaveBeenCalledTimes(2);
  expect(global.browser.storage.local.set).toHaveBeenCalledTimes(1);
});

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
