const { armCaptureBase, failCapture, inRetrievePdfSession, looksPaywalledUrl, processIncomingPdfData, removeSlashes, retrievingAttachment, retrievingPdfFile, sanitizeDOI, startJob, storeDetailsInSessionData }  = require("../src/background.functions");

// not tested (yet): armCaptureBase failCapture saveLog

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
  fakeFilter = {
    disconnect: jest.fn(),
    onstop: jest.fn(),
    write: jest.fn(),
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
  global.captureSession = {
    "expectBrowserDownload": false,
     "doi": "10.1234/foo.bar",
  }
  global.URL = {
    "createObjectURL": jest.fn().mockReturnValue("blob:fake"),
    "revokeObjectURL": jest.fn()
  }

  const details = { requestId: "req-1" };
  processIncomingPdfData(details);

  expect(browser.webRequest.filterResponseData).toHaveBeenCalledWith("req-1");

  // test fakeFilter
  const chunk1 = new Uint8Array([1, 2, 3]);
  const chunk2 = new Uint8Array([4, 5]);
  fakeFilter.ondata({ data: chunk1 });
  fakeFilter.ondata({ data: chunk2 });
  await fakeFilter.onstop();

  expect(fakeFilter.write).toHaveBeenCalledTimes(2);
  expect(fakeFilter.write).toHaveBeenNthCalledWith(1, chunk1);
  expect(fakeFilter.write).toHaveBeenNthCalledWith(2, chunk2);
  expect(fakeFilter.disconnect).toHaveBeenCalled();

  // test object creation
  expect(URL.createObjectURL).toHaveBeenCalledTimes(1);

  // test download
  expect(browser.downloads.download).toHaveBeenCalledWith({
    url: "blob:fake",
    filename: "10.1234_foo.bar.pdf", // DOI with '/' replaced by '_' + ".pdf"
    saveAs: false,
  });

  // test failCapture
  expect(self.failCapture).not.toHaveBeenCalled();
});

test("setting expectBrowserDownload prevents browser download", async () => {
  fakeFilter = { 
    disconnect: jest.fn(), 
    onstop: jest.fn(), 
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

  global.captureSession = {
    "doi": "10.1234/doi",
    "expectBrowserDownload": true
  };
  processIncomingPdfData({ requestId: "req-2" });
  await fakeFilter.onstop();
  expect(browser.downloads.download).not.toHaveBeenCalled();

  global.captureSession["expectBrowserDownload"] = false;
  processIncomingPdfData({ requestId: "req-3" });
  await fakeFilter.onstop();
  expect(browser.downloads.download).toHaveBeenCalled();
});

test("start job",  async() => {
  const doi = "10.1234/foo.bar";
  const url = "https://doi.org/" + doi;
  global.self = {
    sanitizeDOI: (doi) => doi,
    sendStatus: (text) => null,
  }
  global.browser = {
    tabs: { create: jest.fn() },
    storage: { local: { set: jest.fn().mockResolvedValue(undefined) } }
  }
  browser.tabs.create.mockResolvedValue(doi);
 
  await startJob(doi);
  const [ returnValue ] = global.browser.storage.local.set.mock.calls[0];
  expect(returnValue.job.url).toBe(url);
  expect(browser.tabs.create).toHaveBeenCalledWith({ url });
});

test("armCaptureOnly", async() => {
  global.self = { 
    armCaptureBase: jest.fn(),
    sendStatus: jest.fn(), 
  }
  const doi = "doi";
  const tabId = 123;
  const expectedUrl = "https://domain/dir";
  const result = await armCaptureOnly(doi, tabId, expectedUrl);
  expect(result).toBe(true);
  expect(self.sendStatus).toHaveBeenCalledTimes(1);
  expect(self.armCaptureBase).toHaveBeenCalledWith(doi, tabId, expectedUrl);
});

test("armCaptureAndNavigate", async() => {
  global.self = {
    armCaptureBase: jest.fn(),
    sendStatus: jest.fn(), 
  };
  global.browser = {tabs: {update: jest.fn(), }};
  const doi = "doi";
  const tabId = 123;
  const expectedUrl = "https://domain/dir";
  const result = armCaptureAndNavigate(doi, tabId, expectedUrl);
  expect(self.sendStatus).toHaveBeenCalledTimes(1);
  expect(self.armCaptureBase).toHaveBeenCalledWith(doi, tabId, expectedUrl);
  expect(browser.tabs.update).toHaveBeenCalledWith(tabId, {"url": expectedUrl});
});


// function armCaptureAndNavigate(doi, tabId, expectedUrl) {
//   self.sendStatus(`Entering armCaptureAndNavigate for ${expectedUrl}`);
//   self.armCaptureBase(doi, tabId, expectedUrl);
//   return browser.tabs.update(tabId, { url: expectedUrl });
// }
