//change tabs
const categoryTabs = document.querySelectorAll(".searchCategoryTab");
const tabsContent = document.querySelectorAll(".tabsContent");
categoryTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    for (let i = 0, j = categoryTabs.length; i < j; i++) {
      categoryTabs[i].classList.remove("searchCategoryTabActive");
      tabsContent[i].classList.remove("tabsContentActive");
    }
    categoryTabs[tab.dataset.forTab].classList.add("searchCategoryTabActive");
    tabsContent[tab.dataset.forTab].classList.add("tabsContentActive");
  });
});

// main search with autocomplete
document
  .querySelector(".sr_mainSearchWrapper #mainAutocomplete")
  .addEventListener("keyup", async function (e) {
    let search_term = document.querySelector(
      ".sr_mainSearchWrapper #mainAutocomplete"
    ).value;
    if (e.key == "Enter" && search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../search_results/${search_term}`;
    } else {
      let results_list = document.querySelector(
        ".sr_mainSearchWrapper #mainAutocomplete_result"
      );
      if (search_term && search_term.replaceAll(/\s/g, "") != "") {
        try {
          const res = await fetch(
            `../api/search_site/${search_term}`,
            get_fetch_settings("GET")
          );
          if (!res.ok) {
            showMessage(
              "Error: Network request failed unexpectedly!!",
              "Error"
            );
          } else {
            const context = await res.json();
            results_list.style.display = "flex";
            results_list.innerHTML = "";
            if (context[0].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Lists</div>`;
              context[0].forEach((list) => {
                const listRes = `<a href="../list/${list.list_id}" class="searchResult">${list.name}</a>`;
                results_list.innerHTML += listRes;
              });
            }
            if (context[1].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Sources</div>`;
              context[1].forEach((source) => {
                const sourceRes = `<a href="../../sourceprofile/${source.slug}" class="searchResult">${source.slug}</a>`;
                results_list.innerHTML += sourceRes;
              });
            }
            if (context[2].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Articles</div>`;
              context[2].forEach((article) => {
                const articleRes = `<a href="${article.link}" class="searchResult">${article.title}</a>`;
                results_list.innerHTML += articleRes;
              });
            }
          }
        } catch (e) {
          showMessage("Error: Unexpected error has occurred!", "Error");
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
  .querySelector(".sr_mainSearchWrapper .mainSearchContainer i")
  .addEventListener("click", () => {
    search_term = document.querySelector(
      ".sr_mainSearchWrapper .mainInputSearch"
    ).value;
    if (search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../search_results/${search_term}`;
    }
  });
