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
  .querySelector(".searchWrapper #mainAutocomplete")
  .addEventListener("keyup", async function (e) {
    let search_term = document.querySelector(
      ".searchWrapper #mainAutocomplete"
    ).value;
    if (e.key == "Enter" && search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `http://127.0.0.1:8000/search_results/${search_term}`;
    } else {
      let results_list = document.querySelector(
        ".searchWrapper #autocomplete_list_results"
      );
      if (search_term && search_term.replaceAll(/\s/g, "") != "") {
        try {
          const res = await fetch(
            `http://127.0.0.1:8000/api/search_site/${search_term}`,
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
              for (let i = 0, j = context[0].length; i < j; i++) {
                let list = context[0][i];
                let list_url = context[4][i];
                let list_pic;
                if (list.list_pic) {
                  list_pic = list.list_pic;
                } else {
                  list_pic = "/static/home/media/bigger_favicon.png";
                }
                const listRes = `<div class="searchResult"><img src="${list_pic}"><span>${list.name}</span><a href="${list_url}"></a></div>`;
                results_list.innerHTML += listRes;
              }
            }
            if (context[1].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Sources</div>`;
              context[1].forEach((source) => {
                const sourceRes = `<div class="searchResult"><img src="/static/${source.favicon_path}"><span>${source.name}</span><a href="../../source/profile/${source.slug}"></a></div>`;
                results_list.innerHTML += sourceRes;
              });
            }
            if (context[2].length > 0) {
              results_list.innerHTML += `<div class="searchResultHeader">Articles</div>`;
              for (let i = 0, j = context[2].length; i < j; i++) {
                let xfavicon = context[3][i];
                let xtitle = context[2][i].title;
                let xlink = context[2][i].link;
                const articleRes = `<div class="searchResult"><img src="/static/${xfavicon}"><span>${xtitle}</span><a href="${xlink}"></a></div>`;
                results_list.innerHTML += articleRes;
              }
            }
          }
        } catch (e) {
          console.log(e);
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
  .querySelector(".searchWrapper .mainSearchContainer i")
  .addEventListener("click", () => {
    search_term = document.querySelector(
      ".searchWrapper .mainInputSearch"
    ).value;
    if (search_term.replaceAll(/\s/g, "") != "") {
      window.location.href = `../../search_results/${search_term}`;
    }
  });
