document.getElementById("startBtn").addEventListener("click", () => {
  const doi = document.getElementById("doiInput").value.trim();
  const phrase = "PDF"

  if (!doi) {
    alert("Please enter a DOI.");
    return;
  }

  // Prepend your fixed base URL here
  const url = "https://doi.org/" + doi;

  browser.runtime.sendMessage({
    type: "start-job",
    url,
    phrase
  }).catch(err => {
    console.error("[follow-link] error sending start-job:", err);
    alert("Error starting job: " + err);
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
