if (sessionStorage.getItem("listSearchSettings")) {
  const listSearchSettings = JSON.parse(
    sessionStorage.getItem("listSearchSettings")
  );
  document.getElementById("timeframe").value = listSearchSettings[0];
  document.getElementById("content").value = listSearchSettings[1];
  document.getElementById("minimum_rating").value = listSearchSettings[2];
  document.getElementById("primary_source").value = listSearchSettings[3];
  sessionStorage.removeItem("listSearchSettings");
}

//Filter functionality
document.querySelector(".searchButton").addEventListener("click", async () => {
  const timeframeSelect = document.getElementById("timeframe");
  const timeframe =
    timeframeSelect.options[timeframeSelect.selectedIndex].value;
  const contentTypeSelect = document.getElementById("content");
  const contentType =
    contentTypeSelect.options[contentTypeSelect.selectedIndex].value;
  const minimumRatingSelect = document.getElementById("minimum_rating");
  const minimum_rating =
    minimumRatingSelect.options[minimumRatingSelect.selectedIndex].value;
  const primarySourceSelect = document.getElementById("primary_source");
  const primary_source =
    primarySourceSelect.options[primarySourceSelect.selectedIndex].value;
  const listSearchSettings = [
    timeframe,
    contentType,
    minimum_rating,
    primary_source,
  ];
  sessionStorage.setItem(
    "listSearchSettings",
    JSON.stringify(listSearchSettings)
  );
  window.location = `../../../../../../lists/${timeframe}/${contentType}/${minimum_rating}/${primary_source}/`;
});

//open create List Menu
const createListButton = document.querySelector(".createListButton");
createListButton.addEventListener("click", () => {
  if (!createListButton.classList.contains("registrationLink")) {
    document.querySelector(
      ".searchResultsAndListCreationContainer .createListMenu"
    ).style.display = "flex";
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

// list search with autocomplete
document.getElementById("search").addEventListener("keyup", async function (e) {
  let search_term = document.getElementById("search").value;
  if (e.key == "Enter" && search_term.replaceAll(/\s/g, "") != "") {
    window.location.href = `../../../../../../search_results/${search_term}`;
  } else {
    let results_list = document.getElementById("autocomplete_list_results");
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      try {
        const res = await fetch(
          `../../../../../../api/search_lists/${search_term}`,
          get_fetch_settings("GET")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!!", "Error");
        } else {
          const context = await res.json();
          results_list.style.display = "flex";
          results_list.innerHTML = "";
          if (context[0].length > 0) {
            for (let i = 0, j = context[0].length; i < j; i++) {
              let list_pic =
                "https://finbrowser.s3.us-east-2.amazonaws.com/static/home/media/finbrowser-bigger-logo.png";
              if (context[0][i].list_pic) {
                list_pic = context[0][i].list_pic;
              }
              const result = `<div class="searchResult"><img src="${list_pic}"><span>${context[0][i].name}</span><a href="../../../../../..${context[1][i]}"></a></div>`;
              results_list.innerHTML += result;
            }
          }
        }
      } catch (e) {
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
    search_term = document.getElementById("search").value;
    if (search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../../../../../search_results/${search_term}`;
    }
  });
