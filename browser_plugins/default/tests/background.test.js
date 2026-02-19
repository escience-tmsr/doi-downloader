const { failCapture, inRetrievePdfSession, looksPaywalledUrl, removeSlashes, retrievingAttachment, retrievingPdfFile, sanitizeDOI, sendStatus, startJob, storeDetailsInSessionData }  = require("../src/background.functions");

test("removes non-essential characters from DOI", () => {
  expect(sanitizeDOI("doi: https://doi.org/10.1613/jair.1.20161"))
    .toBe("10.1613/jair.1.20161");
});

test("strips doi.org prefix", () => {
  expect(sanitizeDOI("https://doi.org/10.1613/jair.1.20161"))
    .toBe("10.1613/jair.1.20161");
});

test("removes slashes from DOI", () => {
  expect(removeSlashes("10.1613/jair.1.20161"))
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

test("not in retrieve PDF session", () => {
  captureSession = null;
  expect(inRetrievePdfSession(1))
    .toBe(false);
});

test("in retrieve PDF session", () => {
  captureSession = { tabId: 1 };
  expect(inRetrievePdfSession(1))
    .toBe(true);
});

test("not retrieving PDF file", () => {
  expect(retrievingPdfFile({ responseHeaders: null }))
    .toBe(false);
});

test("retrieving PDF file", () => {
  expect(retrievingPdfFile({
         responseHeaders: [ { name: "Content-type", 
                              value: "application/pdf" } ]
         }))
    .toBe(true);
});

test("store details in session data", () => {
  details = { type: "main_frame", 
              url: "url",
              statusCode: "statusCode",
              responseHeaders: [ { name: "Content-type",
                                   value: "Content-type" } ] };
  captureSession = {};
  storeDetailsInSessionData(details);
  expect(Boolean(captureSession.lastMainUrl === details.url &&
         captureSession.lastMainStatus === details.statusCode &&
         captureSession.lastMainContentType === "content-type")).toBe(true);
});

test("not retrieving attachment", () => {
  expect(retrievingAttachment({ responseHeaders: null }))
    .toBe(false);
});

test("retrieving attachment", () => {
  expect(retrievingAttachment({
         responseHeaders: [ { name: "Content-disposition", 
                              value: "attachment" } ]
         }))
    .toBe(true);
});
