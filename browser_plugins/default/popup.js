document.getElementById("startBtn").addEventListener("click", () => {
  const doi = document.getElementById("doiInput").value.trim();
  const phrase = "PDF"
  const url = "https://doi.org/" + doi;

  if (!doi) {
    setStatus("Please enter a DOI.", isError = true);
    return;
  }

  browser.runtime.sendMessage({
    type: "start-job",
    url,
    phrase
  }).catch(err => {
    setStatus("Error starting job: " + err, isError = true);
  });

  browser.runtime.onMessage.addListener((msg) => {
    if (msg?.type === "status") {
      const el = document.getElementById("status");
      if (el) {
        el.textContent = msg.text;
      }
    }
  });
});

function setStatus(text, isError = false) {
  const element = document.getElementById("status");
  if (!element) return;
  element.textContent = text;
  if (!isError) { console.log(text); }
  else {
    element.style.color = "red";
    console.error("[default-extension] " + text);
  }
}
