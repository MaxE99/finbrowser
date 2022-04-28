async function load_filters() {
  try {
    const res = await fetch(
      `../api/get_list_filters`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: List filters couldn't be fetched!", "Error");
    } else {
      const context = await res.json();
      if (context[0] != null) {
        document.getElementById("timeframe").value = context[0];
        document.getElementById("content").value = context[1];
        document.getElementById("minimum_rating").value = context[2];
        document.querySelector("summary").innerText = context[3];
      }
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
}

load_filters();

// Autocomplete for search
document.getElementById("search").addEventListener("keyup", async () => {
  let search_term = document.getElementById("search").value;
  let results_list = document.getElementById("autocomplete_list_results");
  if (search_term && search_term.replaceAll(/\s/g, "") != "") {
    try {
      const res = await fetch(
        `../api/search_lists/${search_term}`,
        get_fetch_settings("GET")
      );
      if (!res.ok) {
        showMessage("Error: List couldn't be filtered!", "Error");
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
  const sources = document.querySelector("summary").innerText;
  try {
    const res = await fetch(
      `../api/filter_list/${timeframe}/${contentType}/${minimum_rating}/${sources}`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: List couldn't be filtered!", "Error");
    } else {
      const context = await res.json();
      window.location.href = "../../lists";
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
});

//open create List Menu
const createListButton = document.querySelector(".createListButton");
createListButton.addEventListener("click", () => {
  if (!createListButton.classList.contains("registrationLink")) {
    document.querySelector(".createListMenu").style.display = "flex";
  }
});
