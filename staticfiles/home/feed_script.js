//check if createListMenu at 7nth spot
function check_interaction_wrapper_at_last_spot(sliderWrapper, closeMenu) {
  spot = sliderWrapper.querySelectorAll(".contentWrapper").length;
  items_per_screen = getComputedStyle(
    sliderWrapper.querySelector(".slider")
  ).getPropertyValue("--items-per-screen");
  if (spot % items_per_screen == 0) {
    if (closeMenu) {
      sliderWrapper.querySelector(".slider").style.zIndex = "";
    } else {
      sliderWrapper.querySelector(".slider").style.zIndex = "1000";
    }
  }
}

// Open create list menu in slider
document
  .querySelector(".sliderWrapper .interactionWrapper .createListButton")
  .addEventListener("click", () => {
    document.querySelector(
      ".interactionWrapper .createListMenu"
    ).style.display = "flex";
    check_interaction_wrapper_at_last_spot(
      document.querySelectorAll(".sliderWrapper")[0],
      false
    );
  });

// Close menus
document
  .querySelector(".interactionWrapper .closeFormContainerButton")
  .addEventListener("click", () => {
    document.querySelector(
      ".interactionWrapper .createListMenu"
    ).style.display = "none";
    check_interaction_wrapper_at_last_spot(
      document.querySelectorAll(".sliderWrapper")[0],
      true
    );
  });

//open add sources menu
if (document.querySelector(".addSourcesButton")) {
  document.querySelector(".addSourcesButton").addEventListener("click", () => {
    document.querySelector(
      ".interactionWrapper .addSourcesForm"
    ).style.display = "flex";
    check_interaction_wrapper_at_last_spot(
      document.querySelectorAll(".sliderWrapper")[2],
      false
    );
  });
}

//close add sources menu
document
  .querySelectorAll(".addSourcesForm .closeFormContainerButton")
  .forEach((element) => {
    element.addEventListener("click", () => {
      element.parentElement.parentElement.parentElement.querySelector(
        ".addSourcesForm"
      ).style.display = "none";
      check_interaction_wrapper_at_last_spot(
        document.querySelectorAll(".sliderWrapper")[2],
        true
      );
    });
  });

// add Sources Search
let selected_sources = [];
document.querySelectorAll(".addSourcesForm #textInput").forEach((element) => {
  element.addEventListener("keyup", async function (e) {
    let search_term = element.value;
    let results_list = element.parentElement.querySelector(
      ".addSourcesForm #searchResultsContainer"
    );
    let selected_list = element.parentElement.querySelector(
      ".addSourcesForm .selectionContainer"
    );
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      results_list.style.display = "block";
      selected_list.style.display = "none";
      try {
        const res = await fetch(
          `../../api/sources/?feed_search=${search_term}`,
          get_fetch_settings("GET")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          const context = await res.json();
          results_list.innerHTML = "";
          const resultHeader = document.createElement("div");
          resultHeader.innerText = "Results:";
          results_list.append(resultHeader);
          if (context.length > 0) {
            context.forEach((source) => {
              if (selected_sources.includes(source.source_id) == false) {
                const searchResult = document.createElement("div");
                searchResult.classList.add("searchResult");
                const resultImage = document.createElement("img");
                resultImage.src = `https://finbrowser.s3.us-east-2.amazonaws.com/static/${source.favicon_path}`;
                const sourceName = document.createElement("span");
                sourceName.innerText = source.name;
                sourceName.id = `source_id_${source.source_id}`;
                searchResult.append(resultImage, sourceName);
                results_list.appendChild(searchResult);
                searchResult.addEventListener(
                  "click",
                  function addSelectedSource() {
                    // Remove the listener from the element the first time the listener is run:
                    searchResult.removeEventListener(
                      "click",
                      addSelectedSource
                    );
                    selected_sources.push(source.source_id);
                    const removeSourceButton = document.createElement("i");
                    removeSourceButton.classList.add("fas", "fa-trash");
                    removeSourceButton.addEventListener("click", () => {
                      removeSourceButton.parentElement.remove();
                      selected_sources = selected_sources.filter(function (e) {
                        return (
                          e.toString() !==
                          removeSourceButton.previousElementSibling.id.split(
                            "#"
                          )[1]
                        );
                      });
                    });
                    searchResult.appendChild(removeSourceButton);
                    selected_list.appendChild(searchResult);
                    results_list.style.display = "none";
                    selected_list.style.display = "block";
                    element.value = "";
                  }
                );
              }
            });
          }
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    } else {
      results_list.style.display = "none";
      selected_list.style.display = "block";
    }
  });
});

// add/confirm sources to user
document
  .querySelectorAll(".addSourcesForm .formSubmitButton")
  .forEach((element) => {
    element.addEventListener("click", async () => {
      if (selected_sources.length) {
        try {
          const res = await fetch(
            `../../api/sources/subscribe_to_sources/${selected_sources}/`,
            get_fetch_settings("POST")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            const context = await res.json();
            showMessage(context, "Success");
            window.location.reload();
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
        }
      } else {
        showMessage("You need to select sources!", "Error");
      }
    });
  });

// add list Search

//open add lists menu
if (document.querySelector(".addListsButton")) {
  document.querySelector(".addListsButton").addEventListener("click", () => {
    document.querySelector(".interactionWrapper .addListsForm").style.display =
      "flex";
    check_interaction_wrapper_at_last_spot(
      document.querySelectorAll(".sliderWrapper")[1],
      false
    );
  });
}

//close add lists menu
document
  .querySelectorAll(".addListsForm .closeFormContainerButton")
  .forEach((element) => {
    element.addEventListener("click", () => {
      element.parentElement.parentElement.parentElement.querySelector(
        ".addListsForm"
      ).style.display = "none";
      check_interaction_wrapper_at_last_spot(
        document.querySelectorAll(".sliderWrapper")[1],
        true
      );
    });
  });

// add lists
let selected_lists = [];
document.querySelectorAll(".addListsForm #textInput").forEach((element) => {
  element.addEventListener("keyup", async function (e) {
    let search_term = element.value;
    let results_list = element.parentElement.querySelector(
      ".addListsForm #searchResultsContainer"
    );
    let selected_list = element.parentElement.querySelector(
      ".addListsForm .selectionContainer"
    );
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      results_list.style.display = "block";
      selected_list.style.display = "none";
      try {
        const res = await fetch(
          `../../api/lists/?feed_search=${search_term}`,
          get_fetch_settings("GET")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          const context = await res.json();
          results_list.innerHTML = "";
          const resultHeader = document.createElement("div");
          resultHeader.innerText = "Results:";
          results_list.append(resultHeader);
          if (context.length > 0) {
            context.forEach((list) => {
              if (selected_lists.includes(list.list_id) == false) {
                const searchResult = document.createElement("div");
                searchResult.classList.add("searchResult");
                const resultImage = document.createElement("img");
                if (list.list_pic) {
                  resultImage.src = list.list_pic;
                } else {
                  resultImage.src =
                    "https://finbrowser.s3.us-east-2.amazonaws.com/static/home/media/finbrowser-bigger-logo.png";
                }
                const listName = document.createElement("span");
                listName.innerText = list.name;
                listName.id = `list_${list.list_id}`;
                searchResult.append(resultImage, listName);
                results_list.appendChild(searchResult);
                searchResult.addEventListener(
                  "click",
                  function addSelectedSource() {
                    // Remove the listener from the element the first time the listener is run:
                    searchResult.removeEventListener(
                      "click",
                      addSelectedSource
                    );
                    selected_lists.push(list.list_id);
                    const removeListButton = document.createElement("i");
                    removeListButton.classList.add("fas", "fa-trash");
                    removeListButton.addEventListener("click", () => {
                      selected_lists = selected_lists.filter(function (e) {
                        return (
                          e.toString() !==
                          removeListButton.previousElementSibling.id.split(
                            "#"
                          )[1]
                        );
                      });
                      removeListButton.parentElement.remove();
                    });
                    searchResult.appendChild(removeListButton);
                    selected_list.appendChild(searchResult);
                    results_list.style.display = "none";
                    selected_list.style.display = "block";
                    element.value = "";
                  }
                );
              }
            });
          }
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    } else {
      results_list.style.display = "none";
      selected_list.style.display = "block";
    }
  });
});

// add/confirm lists
document.querySelectorAll(".addListsForm button").forEach((element) => {
  element.addEventListener("click", async () => {
    if (selected_lists.length) {
      for (let i = 0, j = selected_lists.length; i < j; i++) {
        try {
          const res = await fetch(
            `../../api/lists/${selected_lists[i]}/list_change_subscribtion_status/`,
            get_fetch_settings("POST")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            const context = await res.json();
            showMessage(context, "Success");
            window.location.reload();
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
        }
      }
    } else {
      showMessage("You need to select lists!", "Error");
    }
  });
});
