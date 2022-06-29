if (sessionStorage.getItem("listSearchSettings")) {
  let a = JSON.parse(sessionStorage.getItem("listSearchSettings"));
  (document.getElementById("timeframe").value = a[0]),
    (document.getElementById("content").value = a[1]),
    (document.getElementById("minimum_rating").value = a[2]),
    (document.getElementById("primary_source").value = a[3]),
    sessionStorage.removeItem("listSearchSettings");
}
document.getElementById("search").addEventListener("keyup", async () => {
  let a = document.getElementById("search").value,
    b = document.getElementById("autocomplete_list_results");
  if (a && "" != a.replaceAll(/\s/g, "")) {
    try {
      let c = await fetch(
        `https://finbrowser.io/api/search_lists/${a}`,
        get_fetch_settings("GET")
      );
      if (c.ok) {
        let d = await c.json();
        (b.style.display = "flex"),
          (b.innerHTML = ""),
          d.forEach((a) => {
            let c = "/static/home/media/finbrowser-bigger-logo.png";
            a.list_pic && (c = a.list_pic);
            let d = `<div class="searchResult"><img src="${c}"><span>${a.name}</span><a href="../../list/${a.list_id}"></a></div>`;
            b.innerHTML += d;
          });
      } else
        showMessage("Error: Network request failed unexpectedly!!", "Error");
    } catch (e) {}
    document.onclick = function (a) {
      "autocomplete_list_results" !== a.target.id && (b.style.display = "none");
    };
  } else b.style.display = "none";
}),
  document
    .querySelector(".searchButton")
    .addEventListener("click", async () => {
      let a = document.getElementById("timeframe"),
        b = a.options[a.selectedIndex].value,
        c = document.getElementById("content"),
        d = c.options[c.selectedIndex].value,
        e = document.getElementById("minimum_rating"),
        f = e.options[e.selectedIndex].value,
        g = document.getElementById("primary_source"),
        h = g.options[g.selectedIndex].value,
        i = [b, d, f, h];
      sessionStorage.setItem("listSearchSettings", JSON.stringify(i)),
        (window.location = `https://finbrowser.io/lists/${b}/${d}/${f}/${h}/`);
    });
const createListButton = document.querySelector(".createListButton");
createListButton.addEventListener("click", () => {
  createListButton.classList.contains("registrationLink") ||
    (document.querySelector(
      ".searchResultsAndListCreationContainer .createListMenu"
    ).style.display = "flex");
}),
  document.querySelector(".filterButton").addEventListener("click", () => {
    let a = document.querySelector(".filterBarMenu");
    "flex" == a.style.display
      ? (a.style.display = "none")
      : (a.style.display = "flex");
  });
