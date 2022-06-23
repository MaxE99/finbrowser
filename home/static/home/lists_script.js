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

// Autocomplete for search
document.getElementById("search").addEventListener("keyup", async () => {
  let search_term = document.getElementById("search").value;
  let results_list = document.getElementById("autocomplete_list_results");
  if (search_term && search_term.replaceAll(/\s/g, "") != "") {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/search_lists/${search_term}`,
        get_fetch_settings("GET")
      );
      if (!res.ok) {
        showMessage("Error: Network request failed unexpectedly!!", "Error");
      } else {
        const context = await res.json();
        results_list.style.display = "flex";
        results_list.innerHTML = "";
        context.forEach((list) => {
          let list_pic = "/static/home/media/bigger_favicon.png";
          if (list.list_pic) {
            list_pic = list.list_pic;
          }
          const result = `<div class="searchResult"><img src="${list_pic}"><span>${list.name}</span><a href="../../list/${list.list_id}"></a></div>`;
          results_list.innerHTML += result;
        });
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
});

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
  window.location = `http://127.0.0.1:8000/lists/${timeframe}/${contentType}/${minimum_rating}/${primary_source}/`;
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
