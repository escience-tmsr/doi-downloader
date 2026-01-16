# Default browser extension

This browser extension reads a DOI and tries to download the PDF of the paper associated with the DOI. The advantage of using the extension is that paper PDFs can be retrieved semi-automatically when the browser user has gained access rights to the papers via another tab in the browser. The word *default* in the title refers to the extension not being developed with a specific target website in mind. PDFs of papers will be stored in the user's `Downloads` directory. 

## Usage

The browser extension was developed for and tested in the [Firefox](https://www.firefox.com) browser. Before being able to process a DOI, the extension needs to be installed in the browser:

1. Open [about:debugging](about:debugging) in the address bar of Firefox
2. Click on `This Firefox` in the left menu
3. Click on the button `Load Temporary Add-on`
4. Open the file `manifest.json`, it should be available from your computer disk together with the other files from this directory

After these four steps, the extension can be used for accessing paper PDFs via their DOIs:

1. Access the extension by clicking on the jigsaw puzzle piece logo in the top right of the browser window: ![](../images/puzzle_piece.png "")
2. A popup window appears, open the extension by clicking on its name: `Default extension`
3. Fill in a DOI under `DOI` and click on the `Go` button. Here is an example DOI from the open access journal [JAIR](https://jair.org): 10.1613/jair.1.18675

The extension will open the main web page associated with DOI, look for a PDF download button on the page and try to download the PDF linked from the page. If successful, the PDF will be stored in the `Downloads` directory of the browser user with the DOI as name (slashes replaced by underscores). The extension displays it progress at the bottom of its popup window. When downloading fails, an error message will be displayed. 

## Links

* Icon source: [Google icons](https://fonts.google.com/icons)
