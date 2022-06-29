document
  .querySelector(".interactionWrapper .createListButton")
  .addEventListener("click", () => {
    check_device_width_below(500)
      ? (document.querySelector(".smartphoneCreateListMenu").style.display =
          "flex")
      : (document.querySelector(
          ".interactionWrapper .createListMenu"
        ).style.display = "flex");
  }),
  document
    .querySelector(".interactionWrapper .closeFormContainerButton")
    .addEventListener("click", () => {
      document.querySelector(
        ".interactionWrapper .createListMenu"
      ).style.display = "none";
    }),
  document.querySelector(".addSourcesButton") &&
    document
      .querySelector(".addSourcesButton")
      .addEventListener("click", () => {
        check_device_width_below(500)
          ? (document.querySelector(".smartphoneAddSourcesForm").style.display =
              "flex")
          : (document.querySelector(".addSourcesForm").style.display = "flex");
      }),
  document
    .querySelector(".addSourcesForm .closeFormContainerButton")
    .addEventListener("click", () => {
      document.querySelector(".addSourcesForm").style.display = "none";
    });
let selected_sources = [];
document
  .querySelector(".addSourcesForm #textInput")
  .addEventListener("keyup", async function (g) {
    let b = document.querySelector(".addSourcesForm #textInput").value,
      a = document.querySelector(".addSourcesForm #searchResultsContainer"),
      c = document.querySelector(".addSourcesForm .selectionContainer");
    if (b && "" != b.replaceAll(/\s/g, "")) {
      (a.style.display = "block"), (c.style.display = "none");
      try {
        let d = await fetch(
          `https://finbrowser.io/api/sources/?feed_search=${b}`,
          get_fetch_settings("GET")
        );
        if (d.ok) {
          let e = await d.json();
          a.innerHTML = "";
          let f = document.createElement("div");
          (f.innerText = "Results:"),
            a.append(f),
            e.length > 0 &&
              e.forEach((b) => {
                if (!1 == selected_sources.includes(b.source_id)) {
                  let d = document.createElement("div");
                  d.classList.add("searchResult");
                  let f = document.createElement("img");
                  f.src = `/static/${b.favicon_path}`;
                  let e = document.createElement("span");
                  (e.innerText = b.name),
                    (e.id = `source_id_${b.source_id}`),
                    d.append(f, e),
                    a.appendChild(d),
                    d.addEventListener("click", function f() {
                      d.removeEventListener("click", f),
                        selected_sources.push(b.source_id);
                      let e = document.createElement("i");
                      e.classList.add("fas", "fa-trash"),
                        e.addEventListener("click", () => {
                          e.parentElement.remove(),
                            (selected_sources = selected_sources.filter(
                              function (a) {
                                return (
                                  a.toString() !==
                                  e.previousElementSibling.id.replace(
                                    "source_id_",
                                    ""
                                  )
                                );
                              }
                            ));
                        }),
                        d.appendChild(e),
                        c.appendChild(d),
                        (a.style.display = "none"),
                        (c.style.display = "block"),
                        (document.querySelector(
                          ".addSourcesForm #textInput"
                        ).value = "");
                    });
                }
              });
        } else
          showMessage("Error: Network request failed unexpectedly!", "Error");
      } catch (h) {}
    } else (a.style.display = "none"), (c.style.display = "block");
  }),
  document
    .querySelector(".addSourcesForm .formSubmitButton")
    .addEventListener("click", async () => {
      if (selected_sources.length)
        try {
          let a = await fetch(
            `https://finbrowser.io/api/sources/subscribe_to_sources/${selected_sources}/`,
            get_fetch_settings("POST")
          );
          if (a.ok) {
            let b = await a.json();
            showMessage(b, "Success"), window.location.reload();
          } else
            showMessage("Error: Network request failed unexpectedly!", "Error");
        } catch (c) {}
      else showMessage("You need to select sources!", "Error");
    }),
  document.querySelector(".addListsButton") &&
    document.querySelector(".addListsButton").addEventListener("click", () => {
      check_device_width_below(500)
        ? (document.querySelector(".smartphoneAddListsForm").style.display =
            "flex")
        : (document.querySelector(".addListsForm").style.display = "flex");
    }),
  document
    .querySelector(".addListsForm .closeFormContainerButton")
    .addEventListener("click", () => {
      document.querySelector(".addListsForm").style.display = "none";
    });
let selected_lists = [];
document
  .querySelector(".addListsForm #textInput")
  .addEventListener("keyup", async function (g) {
    let b = document.querySelector(".addListsForm #textInput").value,
      a = document.querySelector(".addListsForm #searchResultsContainer"),
      c = document.querySelector(".addListsForm .selectionContainer");
    if (b && "" != b.replaceAll(/\s/g, "")) {
      (a.style.display = "block"), (c.style.display = "none");
      try {
        let d = await fetch(
          `https://finbrowser.io/api/lists/?feed_search=${b}`,
          get_fetch_settings("GET")
        );
        if (d.ok) {
          let e = await d.json();
          a.innerHTML = "";
          let f = document.createElement("div");
          (f.innerText = "Results:"),
            a.append(f),
            e.length > 0 &&
              e.forEach((b) => {
                if (!1 == selected_lists.includes(b.list_id)) {
                  let d = document.createElement("div");
                  d.classList.add("searchResult");
                  let e = document.createElement("img");
                  b.list_pic
                    ? (e.src = b.list_pic)
                    : (e.src = "/static/home/media/finbrowser-bigger-logo.png");
                  let f = document.createElement("span");
                  (f.innerText = b.name),
                    (f.id = `list_${b.list_id}`),
                    d.append(e, f),
                    a.appendChild(d),
                    d.addEventListener("click", function f() {
                      d.removeEventListener("click", f),
                        selected_lists.push(b.list_id);
                      let e = document.createElement("i");
                      e.classList.add("fas", "fa-trash"),
                        e.addEventListener("click", () => {
                          (selected_lists = selected_lists.filter(function (a) {
                            return (
                              a.toString() !==
                              e.previousElementSibling.id.replace("list_", "")
                            );
                          })),
                            e.parentElement.remove();
                        }),
                        d.appendChild(e),
                        c.appendChild(d),
                        (a.style.display = "none"),
                        (c.style.display = "block"),
                        (document.querySelector(
                          ".addListsForm #textInput"
                        ).value = "");
                    });
                }
              });
        } else
          showMessage("Error: Network request failed unexpectedly!", "Error");
      } catch (h) {}
    } else (a.style.display = "none"), (c.style.display = "block");
  }),
  document
    .querySelector(".addListsForm button")
    .addEventListener("click", async () => {
      if (selected_lists.length)
        for (let a = 0, c = selected_lists.length; a < c; a++)
          try {
            let b = await fetch(
              `https://finbrowser.io/api/lists/${selected_lists[a]}/list_change_subscribtion_status/`,
              get_fetch_settings("POST")
            );
            if (b.ok) {
              let d = await b.json();
              showMessage(d, "Success"), window.location.reload();
            } else
              showMessage(
                "Error: Network request failed unexpectedly!",
                "Error"
              );
          } catch (e) {}
      else showMessage("You need to select lists!", "Error");
    }),
  document.querySelector(".addExternalLinkButton") &&
    document
      .querySelector(".addExternalLinkButton")
      .addEventListener("click", () => {
        document.querySelector(".addExternalLinksContainer").style.display =
          "flex";
      }),
  document
    .querySelector(".addExternalLinksContainer .closeFormContainerButton")
    .addEventListener("click", () => {
      document.querySelector(".addExternalLinksContainer").style.display =
        "none";
    });
