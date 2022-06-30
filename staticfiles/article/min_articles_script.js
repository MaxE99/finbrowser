if (sessionStorage.getItem("articleSearchSettings")) {
  let a = JSON.parse(sessionStorage.getItem("articleSearchSettings"));
  (document.getElementById("timeframe").value = a[0]),
    (document.getElementById("sector").value = a[1]),
    (document.getElementById("paywall").value = a[2]),
    (document.getElementById("source").value = a[3]),
    sessionStorage.removeItem("articleSearchSettings");
}
document.querySelector(".searchButton").addEventListener("click", async () => {
  let a = document.getElementById("timeframe"),
    b = a.options[a.selectedIndex].value,
    c = document.getElementById("sector"),
    d = c.options[c.selectedIndex].value,
    e = document.getElementById("paywall"),
    f = e.options[e.selectedIndex].value,
    g = document.getElementById("source"),
    h = g.options[g.selectedIndex].value,
    i = [b, d, f, h];
  sessionStorage.setItem("articleSearchSettings", JSON.stringify(i)),
    (window.location = `https://www.finbrowser.io/articles/${b}/${d}/${f}/${h}`);
}),
  document.getElementById("search").addEventListener("keyup", async () => {
    let d = document.getElementById("search").value,
      c = document.getElementById("autocomplete_list_results");
    if (d && "" != d.replaceAll(/\s/g, "")) {
      try {
        let e = await fetch(
          `https://www.finbrowser.io/api/search_articles/${d}`,
          get_fetch_settings("GET")
        );
        if (e.ok) {
          let a = await e.json();
          if (((c.style.display = "flex"), (c.innerHTML = ""), a[0].length > 0))
            for (let b = 0, f = a[0].length; b < f; b++) {
              let g = a[1][b],
                h = a[0][b].title,
                i = a[0][b].link,
                j = `<div class="searchResult"><img src="/static/${g}"><span>${h}</span><a href="${i}"></a></div>`;
              c.innerHTML += j;
            }
        } else
          showMessage("Error: Network request failed unexpectedly!", "Error");
      } catch (k) {}
      document.onclick = function (a) {
        "autocomplete_list_results" !== a.target.id &&
          (c.style.display = "none");
      };
    } else c.style.display = "none";
  }),
  document.querySelector(".filterButton").addEventListener("click", () => {
    let a = document.querySelector(".filterBarMenu");
    "flex" == a.style.display
      ? (a.style.display = "none")
      : (a.style.display = "flex");
  });
