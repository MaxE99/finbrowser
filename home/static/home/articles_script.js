async function load_filters() {
  try {
    const res = await fetch(
      `../api/get_article_filters`,
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
      `../api/filter_articles/${timeframe}/${sector}/${paywall}/${sources}`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: List couldn't be filtered!", "Error");
    } else {
      const context = await res.json();
      window.location.href = "../../articles";
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
});

// Autocomplete for search
document.getElementById("search").addEventListener("keyup", async () => {
  let search_term = document.getElementById("search").value;
  let results_list = document.getElementById("autocomplete_list_results");
  if (search_term && search_term.replaceAll(/\s/g, "") != "") {
    try {
      const res = await fetch(
        `../api/search_articles/${search_term}`,
        get_fetch_settings("GET")
      );
      if (!res.ok) {
        showMessage("Error: List couldn't be filtered!", "Error");
      } else {
        const context = await res.json();
        results_list.style.display = "flex";
        results_list.innerHTML = "";
        if (context[0].length > 0) {
          for (let i = 0, j = context[0].length; i < j; i++) {
            let favicon = context[1][i];
            let title = context[0][i].title;
            let link = context[0][i].link;
            const articleRes = `<div class="searchResult"><img src="/static/${favicon}"><span>${title}</span><a href="${link}"></a></div>`;
            results_list.innerHTML += articleRes;
          }
        }
      }
    } catch (e) {
      showMessage("Error: Network error detected!", "Error");
    }
    document.onclick = function (e) {
      if (e.target.id !== "autocomplete_list_results") {
        results_list.style.display = "none";
      }
    };
  } else {
    results_list.style.display = "none";
  }
});
