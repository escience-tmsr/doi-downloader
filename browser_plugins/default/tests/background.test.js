const { failCapture, looksPaywalledUrl, sanitizeDOI, sendStatus, startJob }  = require("../src/background.functions");

test("sanitizes DOI into filesystem-safe name", () => {
  expect(sanitizeDOI("10.1613/jair.1.20161"))
    .toBe("10.1613_jair.1.20161");
});

test("strips doi.org prefix", () => {
  expect(sanitizeDOI("https://doi.org/10.1613/jair.1.20161"))
    .toBe("10.1613_jair.1.20161");
});

test("text with paywall words 1/2", () => {
  expect(looksPaywalledUrl("https://domain/some_paywall_file"))
    .toBe(true);
});

test("text with paywall words 2/2", () => {
  expect(looksPaywalledUrl("https://domain/some_account_file"))
    .toBe(true);
});

test("text without paywall words", () => {
  expect(looksPaywalledUrl("https://domain/no_special_file"))
    .toBe(false);
});

test("failCapture", () => {
  expect(failCapture("something", "some text"))
    .toBe(null);
});