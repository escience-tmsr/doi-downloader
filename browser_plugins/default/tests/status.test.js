require("jest-webextension-mock");

const { setBadge, sendStatus }  = require("../src/status");

test("set badge text", () => {
  const dot = "•";
  setBadge(dot, false);
  expect(browser.browserAction.setBadgeText).toHaveBeenCalledWith({ text: dot });
});

test("set status text", () => {
  const text = "text";
  const dot = "•";
  sendStatus(text, false);
  expect(browser.browserAction.setBadgeText).toHaveBeenCalledWith({ text: dot });
  expect(browser.runtime.sendMessage).toHaveBeenCalledWith({ type: "status", text: text });
});
