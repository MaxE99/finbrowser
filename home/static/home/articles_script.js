if (sessionStorage.getItem("articleSearchSettings")) {
  const articleSearchSettings = JSON.parse(
    sessionStorage.getItem("articleSearchSettings")
  );
  document.getElementById("timeframe").value = articleSearchSettings[0];
  document.getElementById("sector").value = articleSearchSettings[1];
  document.getElementById("paywall").value = articleSearchSettings[2];
  document.getElementById("source").value = articleSearchSettings[3];
  sessionStorage.removeItem("articleSearchSettings");
}

//Filter functionality
document.querySelector(".searchButton").addEventListener("click", async () => {
  const timeframeSelect = document.getElementById("timeframe");
  const timeframe =
    timeframeSelect.options[timeframeSelect.selectedIndex].value;
  const sectorSelect = document.getElementById("sector");
  const sector = sectorSelect.options[sectorSelect.selectedIndex].value;
  const paywallSelect = document.getElementById("paywall");
  const paywall = paywallSelect.options[paywallSelect.selectedIndex].value;
  const sourceSelect = document.getElementById("source");
  const source = sourceSelect.options[sourceSelect.selectedIndex].value;
  const articleSearchSettings = [timeframe, sector, paywall, source];
  sessionStorage.setItem(
    "articleSearchSettings",
    JSON.stringify(articleSearchSettings)
  );
  window.location = `http://127.0.0.1:8000/articles/${timeframe}/${sector}/${paywall}/${source}`;
});

// Autocomplete for search
document.getElementById("search").addEventListener("keyup", async () => {
  let search_term = document.getElementById("search").value;
  let results_list = document.getElementById("autocomplete_list_results");
  if (search_term && search_term.replaceAll(/\s/g, "") != "") {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/search_articles/${search_term}`,
        get_fetch_settings("GET")
      );
      if (!res.ok) {
        showMessage("Error: Network request failed unexpectedly!", "Error");
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
      // showMessage("Error: Unexpected error has occurred!", "Error");
    }
    // closes list results list when user clicks somewhere else on the page
    document.onclick = function (e) {
      if (e.target.id !== "autocomplete_list_results") {
        results_list.style.display = "none";
      }
    };
  } else {
    results_list.style.display = "none";
  }
});

//Toggle Filter Menu
document.querySelector(".filterButton").addEventListener("click", () => {
  const filterBarMenu = document.querySelector(".filterBarMenu");
  if (filterBarMenu.style.display == "flex") {
    filterBarMenu.style.display = "none";
  } else {
    filterBarMenu.style.display = "flex";
  }
});
