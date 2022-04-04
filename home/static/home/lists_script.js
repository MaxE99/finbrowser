async function load_filters() {
  try {
    const res = await fetch(`../get_list_filters`, get_fetch_settings("GET"));
    if (!res.ok) {
      showMessage("Error: List filters couldn't be fetched!", "Error");
    } else {
      const context = await res.json();
      if (context[0] != null) {
        document.getElementById("timeframe").value = context[0];
        document.getElementById("content").value = context[1];
        document.getElementById("sources").value = context[2];
      }
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
}

load_filters();

const createListMenu = document.querySelector(".createListMenu");
const overlay = document.querySelector(".overlay");

// Open settings menu
document.querySelector(".createListButton").addEventListener("click", () => {
  overlay.style.opacity = "0.5";
  createListMenu.style.display = "flex";
});

// Close menus
document
  .querySelectorAll(".closeMenuButton, .closeButton")
  .forEach((button) => {
    button.addEventListener("click", () => {
      overlay.style.opacity = "1";
      document.querySelectorAll(".popUpMenu").forEach((menu) => {
        menu.style.display = "none";
      });
    });
  });

// Autocomplete for search
document.getElementById("search").addEventListener("keyup", async () => {
  let search_term = document.getElementById("search").value;
  let results_list = document.getElementById("autocomplete_list_results");
  if (search_term && search_term.replaceAll(/\s/g, "") != "") {
    try {
      const res = await fetch(
        `../search_lists/${search_term}`,
        get_fetch_settings("GET")
      );
      if (!res.ok) {
        showMessage("Error: List couldn't be filtered!", "Error");
      } else {
        const context = await res.json();
        results_list.style.display = "flex";
        results_list.innerHTML = "";
        context.forEach((list) => {
          const result = `<a href="../list/${list.list_id}" class="searchResult">${list.name}</a>`;
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
    contentTypeSelect.options[contentTypeSelect.selectedIndex].innerText;
  const sourcesSelect = document.getElementById("sources");
  const sources = sourcesSelect.options[sourcesSelect.selectedIndex].innerText;
  try {
    const res = await fetch(
      `../filter_list/${timeframe}/${contentType}/${sources}`,
      get_fetch_settings("GET")
    );
    if (!res.ok) {
      showMessage("Error: List couldn't be filtered!", "Error");
    } else {
      const context = await res.json();
      window.location.href = "../../home/lists";
    }
  } catch (e) {
    showMessage("Error: Network error detected!", "Error");
  }
});
