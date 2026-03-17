require("jest-webextension-mock");

const { setBadge, sendStatus }  = require("../src/status");

test("set badge text", () => {
  const dot = "•";
  global.browser = {"browserAction": {
    "setBadgeBackgroundColor": jest.fn(),
    "setBadgeText": jest.fn(),
  }}
  let isError = false;
  let result = setBadge(dot, isError);
  expect(browser.browserAction.setBadgeText).toHaveBeenCalledWith({ text: dot });
  expect(browser.browserAction.setBadgeBackgroundColor).toHaveBeenCalledTimes(1);
  expect(result).toBe(isError);

  isError = true;
  result = setBadge(dot, isError);
  expect(result).toBe(isError);
});

test("sendStatus", () => {
  const text = "text";
  const dot = "•";
  global.self = {"setBadge": jest.fn()};
  global.browser = {
    "runtime": {"sendMessage": jest.fn().mockResolvedValue(undefined)},
  };
  global.console = {
    "error": jest.fn(),
    "log": jest.fn(),
  };
  let result = sendStatus(text);
  expect(self.setBadge).toHaveBeenCalledWith(dot, false);
  expect(console.log).toHaveBeenCalledTimes(1);
  expect(browser.runtime.sendMessage).toHaveBeenCalledWith({ type: "status", text: text });
  expect(result).toBe(null);

  let element = {"textContent": "", "style": {"color": ""},}
  document.getElementById = jest.fn().mockReturnValue(element);
  result = sendStatus(text, true);
  expect(console.error).toHaveBeenCalledTimes(1);
  expect(result).not.toBe(null);
  expect(element.textContent).toBe(text);
  expect(element.style.color).toBe("red");

  result = sendStatus(text, false);
  expect(element.style.color).toBe("");
  expect(result).not.toBe(null);

  document.getElementById = jest.fn().mockReturnValue(null);
  result = sendStatus(text, false);
  expect(result).toBe(null);
});
