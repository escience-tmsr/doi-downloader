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

  browser.runtime.sendMessage = jest.fn().mockRejectedValue(new Error("error"));
  self.sendStatus.mockClear();
  result = await performAction(job, myTabId);
  expect(result).toBe("error");
  expect(self.sendStatus).toHaveBeenCalledWith(expect.stringMatching("^Error"));
  expect(self.sendStatus).toHaveBeenCalledTimes(3);

  browser.runtime.sendMessage = jest.fn().mockResolvedValue();
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
    "used": false,
    "usedUrl": [],
  }          
  global.browser = {"storage": {"local": {
    "get": jest.fn().mockResolvedValue({"job": job}),
    "set": jest.fn().mockResolvedValue(),
  }}};
  global.locations = {"href": "here-1"};
  self.sendStatus = jest.fn();
  let result = await maybeRunJob(myTabId);
  expect(result).toBe("finished job");
  expect(self.sendStatus).toHaveBeenCalledTimes(2);
  expect(global.browser.storage.local.set).toHaveBeenCalledTimes(1);

  result = await maybeRunJob(myTabId);
  expect(result).toBe("processed job");

  jest.useFakeTimers();
  job = {
    "tabId": myTabId,
    "used": false,
    "usedUrl": [],
  }
  global.browser.storage.local. get = jest.fn().mockResolvedValue({"job": job});
  global.locations = {"href": "here-2"};
  self.performAction = jest.fn();
  self.sendStatus.mockClear();
  result = await maybeRunJob(myTabId);
  jest.runAllTimers();
  expect(result).toBe("finished job");
  expect(self.sendStatus).toHaveBeenCalledTimes(2);
  jest.useRealTimers();
});
