const { failCapture, inRetrievePdfSession, looksPaywalledUrl, processIncomingPdfData, removeSlashes, retrievingAttachment, retrievingPdfFile, sanitizeDOI, sendStatus, startJob, storeDetailsInSessionData }  = require("../src/background.functions");

// not tested (yet): armCapture* (3) startJob failCapture saveLog

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

test("streams PDF data and triggers a download when expectBrowserDownload is false", async () => {
  const details = { requestId: "req-1" };
  fakeFilter = {
    disconnect: function onstop_function() {},
    onstop: function onstop_function() {},
  };
  global.browser = {
    webRequest: { filterResponseData: jest.fn().mockReturnValue(fakeFilter) },
    downloads: { download: jest.fn().mockResolvedValue(123) }
  };
  global.self = {
    sanitizeDOI: (doi) => doi,
    removeSlashes: (s) => s.replace(/\//g, "_"),
    failCapture: jest.fn(),
  };
  global.captureSession["expectBrowserDownload"] = false;
  processIncomingPdfData({ requestId: "req-3" });

  processIncomingPdfData(details);

  expect(browser.webRequest.filterResponseData).toHaveBeenCalledWith("req-1");

  const chunk1 = new Uint8Array([1, 2, 3]);
  const chunk2 = new Uint8Array([4, 5]);

  // The function we passed into ondata is stored on fakeFilter.ondata
  fakeFilter.ondata({ data: chunk1 });
  fakeFilter.ondata({ data: chunk2 });

  // Now simulate the response finishing
  await fakeFilter.onstop();

  // We should have forwarded both chunks to the browser
  expect(fakeFilter.write).toHaveBeenCalledTimes(2);
  expect(fakeFilter.write).toHaveBeenNthCalledWith(1, chunk1);
  expect(fakeFilter.write).toHaveBeenNthCalledWith(2, chunk2);

  // The filter should be disconnected
  expect(fakeFilter.disconnect).toHaveBeenCalled();

  // A Blob URL should be created
  expect(URL.createObjectURL).toHaveBeenCalledTimes(1);

  // And a download should be triggered with the sanitized filename
  expect(browser.downloads.download).toHaveBeenCalledWith({
    url: "blob:fake",
    filename: "10.1234_foo.bar.pdf", // DOI with '/' replaced by '_' + ".pdf"
    saveAs: false,
  });

  // We don't expect failCapture to be called in the success case
  expect(self.failCapture).not.toHaveBeenCalled();
});

test("setting expectBrowserDownload prevents browser download", async () => {
  fakeFilter = { 
    disconnect: function onstop_function() {}, 
    onstop: function onstop_function() {}, 
  };
  global.browser = {
    webRequest: { filterResponseData: jest.fn().mockReturnValue(fakeFilter) },
    downloads: { download: jest.fn().mockResolvedValue(123) }
  };
  global.self = {
    sanitizeDOI: (doi) => doi,
    removeSlashes: (s) => s.replace(/\//g, "_"),
    failCapture: jest.fn(),
  };

  global.captureSession = { "doi": "10.1234/doi" };
  global.captureSession["expectBrowserDownload"] = true;
  processIncomingPdfData({ requestId: "req-2" });
  await fakeFilter.onstop();
  expect(browser.downloads.download).not.toHaveBeenCalled();

  global.captureSession["expectBrowserDownload"] = false;
  processIncomingPdfData({ requestId: "req-3" });
  await fakeFilter.onstop();
  expect(browser.downloads.download).toHaveBeenCalled();
});
