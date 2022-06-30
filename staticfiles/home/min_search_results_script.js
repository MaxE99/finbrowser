const categoryTabs = document.querySelectorAll(".searchCategoryTab"),
  tabsContent = document.querySelectorAll(".tabsContent");
categoryTabs.forEach((a) => {
  a.addEventListener("click", () => {
    for (let b = 0, c = categoryTabs.length; b < c; b++)
      categoryTabs[b].classList.remove("searchCategoryTabActive"),
        tabsContent[b].classList.remove("tabsContentActive");
    categoryTabs[a.dataset.forTab].classList.add("searchCategoryTabActive"),
      tabsContent[a.dataset.forTab].classList.add("tabsContentActive");
  });
}),
  document
    .querySelector(".searchWrapper #mainAutocomplete")
    .addEventListener("keyup", async function (i) {
      let c = document.querySelector(".searchWrapper #mainAutocomplete").value;
      if ("Enter" == i.key && "" != c.replaceAll(/\s/g, ""))
        window.location.href = `https://www.finbrowser.io/search_results/${c}`;
      else {
        let b = document.querySelector(
          ".searchWrapper #autocomplete_list_results"
        );
        if (c && "" != c.replaceAll(/\s/g, "")) {
          try {
            let g = await fetch(
              `https://www.finbrowser.io/api/search_site/${c}`,
              get_fetch_settings("GET")
            );
            if (g.ok) {
              let a = await g.json();
              if (
                ((b.style.display = "flex"),
                (b.innerHTML = ""),
                a[0].length > 0)
              ) {
                b.innerHTML += '<div class="searchResultHeader">Lists</div>';
                for (let e = 0, j = a[0].length; e < j; e++) {
                  let f = a[0][e],
                    k = a[4][e],
                    h;
                  h = f.list_pic
                    ? f.list_pic
                    : "/static/home/media/finbrowser-bigger-logo.png";
                  let l = `<div class="searchResult"><img src="${h}"><span>${f.name}</span><a href="${k}"></a></div>`;
                  b.innerHTML += l;
                }
              }
              if (
                (a[1].length > 0 &&
                  ((b.innerHTML +=
                    '<div class="searchResultHeader">Sources</div>'),
                  a[1].forEach((a) => {
                    let c = `<div class="searchResult"><img src="/static/${a.favicon_path}"><span>${a.name}</span><a href="../../source/profile/${a.slug}"></a></div>`;
                    b.innerHTML += c;
                  })),
                a[2].length > 0)
              ) {
                b.innerHTML += '<div class="searchResultHeader">Articles</div>';
                for (let d = 0, m = a[2].length; d < m; d++) {
                  let n = a[3][d],
                    o = a[2][d].title,
                    p = a[2][d].link,
                    q = `<div class="searchResult"><img src="/static/${n}"><span>${o}</span><a href="${p}"></a></div>`;
                  b.innerHTML += q;
                }
              }
            } else
              showMessage(
                "Error: Network request failed unexpectedly!!",
                "Error"
              );
          } catch (r) {}
          document.onclick = function (a) {
            "autocomplete_list_results" !== a.target.id &&
              (b.style.display = "none");
          };
        } else b.style.display = "none";
      }
    }),
  document
    .querySelector(".searchWrapper .mainSearchContainer i")
    .addEventListener("click", () => {
      "" !=
        (search_term = document.querySelector(
          ".searchWrapper .mainInputSearch"
        ).value).replaceAll(/\s/g, "") &&
        (window.location.href = `https://www.finbrowser.io/search_results/${search_term}`);
    });
