if (sessionStorage.getItem("listSearchSettings")) {
  const listSearchSettings = JSON.parse(
    sessionStorage.getItem("listSearchSettings")
  );
  document.getElementById("paywall").value = listSearchSettings[0];
  document.getElementById("type").value = listSearchSettings[1];
  document.getElementById("minimum_rating").value = listSearchSettings[2];
  document.getElementById("website").value = listSearchSettings[3];
  sessionStorage.removeItem("listSearchSettings");
}

//Filter functionality
document.querySelector(".searchButton").addEventListener("click", async () => {
  const paywallSelect = document.getElementById("paywall");
  const paywall = paywallSelect.options[paywallSelect.selectedIndex].value;
  const typeSelect = document.getElementById("type");
  const type = typeSelect.options[typeSelect.selectedIndex].value;
  const minimumRatingSelect = document.getElementById("minimum_rating");
  const minimum_rating =
    minimumRatingSelect.options[minimumRatingSelect.selectedIndex].value;
  const websiteSelect = document.getElementById("website");
  const website = websiteSelect.options[websiteSelect.selectedIndex].value;
  const listSearchSettings = [paywall, type, minimum_rating, website];
  sessionStorage.setItem(
    "listSearchSettings",
    JSON.stringify(listSearchSettings)
  );
  window.location = `../../../../../../sectors/${paywall}/${type}/${minimum_rating}/${website}/`;
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

// source search with autocomplete
document.getElementById("search").addEventListener("keyup", async function (e) {
  let search_term = document.getElementById("search").value;
  if (e.key == "Enter" && search_term.replaceAll(/\s/g, "") != "") {
    window.location.href = `../../../../../../search_results/${search_term}`;
  } else {
    let results_list = document.getElementById("autocomplete_list_results");
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      try {
        const res = await fetch(
          `../../../../../../api/sources/?sectors_search=${search_term}`,
          get_fetch_settings("GET")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!!", "Error");
        } else {
          const context = await res.json();
          results_list.style.display = "flex";
          results_list.innerHTML = "";
          if (context.length > 0) {
            context.forEach((source) => {
              const result = `<div class="searchResult"><img src="https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}"><span>${source.name}</span><a href="../../source/${source.slug}"></a></div>`;
              results_list.innerHTML += result;
            });
          }
        }
      } catch (e) {
        console.log(e);
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
      document.onclick = function (e) {
        if (e.target.id !== "autocomplete_list_results") {
          results_list.style.display = "none";
        }
      };
    } else {
      results_list.style.display = "none";
    }
  }
});

//get search results
document
  .querySelector(".searchSelectContainer i")
  .addEventListener("click", () => {
    console.log("clicked");
    search_term = document.getElementById("search").value;
    if (search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../../../../../search_results/${search_term}`;
    }
  });
