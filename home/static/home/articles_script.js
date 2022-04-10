async function load_filters() {
  try {
    const res = await fetch(
      `../get_article_filters`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: Article filters couldn't be fetched!", "Error");
    } else {
      const context = await res.json();
      if (context[0] != null) {
        document.getElementById("timeframe").value = context[0];
        document.getElementById("sector").value = context[1];
        document.getElementById("paywall").value = context[2];
        document.querySelector("summary").innerText = context[3];
      }
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
}

load_filters();

//Filter functionality
document.querySelector(".searchButton").addEventListener("click", async () => {
  const timeframeSelect = document.getElementById("timeframe");
  const timeframe =
    timeframeSelect.options[timeframeSelect.selectedIndex].value;
  const sectorSelect = document.getElementById("sector");
  const sector = sectorSelect.options[sectorSelect.selectedIndex].value;
  const paywallSelect = document.getElementById("paywall");
  const paywall = paywallSelect.options[paywallSelect.selectedIndex].value;
  const sources = document.querySelector("summary").innerText;
  try {
    const res = await fetch(
      `../filter_articles/${timeframe}/${sector}/${paywall}/${sources}`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: List couldn't be filtered!", "Error");
    } else {
      const context = await res.json();
      window.location.href = "../../home/articles";
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
});

// select sources
document.querySelectorAll(".selectContainer ul li").forEach((choice) => {
  choice.addEventListener("click", () => {
    document.querySelector("summary").innerText = choice.lastChild.innerText;
    document.querySelector("details").removeAttribute("open");
  });
});
