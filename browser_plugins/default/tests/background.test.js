const { sanitizeDOI, sendStatus, startJob }  = require("../src/background.functions");

test("sanitizes DOI into filesystem-safe name", () => {
  expect(sanitizeDOI("10.1613/jair.1.20161"))
    .toBe("10.1613_jair.1.20161");
});

test("strips doi.org prefix", () => {
  expect(sanitizeDOI("https://doi.org/10.1613/jair.1.20161"))
    .toBe("10.1613_jair.1.20161");
});
