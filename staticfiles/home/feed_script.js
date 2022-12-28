// subscribed lists

document.querySelectorAll(".listSubscribeButton").forEach((subscribeButton) => {
  if (subscribeButton) {
    subscribeButton.addEventListener("click", async () => {
      if (!subscribeButton.classList.contains("registrationLink")) {
        try {
          const list_id = subscribeButton
            .closest(".contentWrapper")
            .id.split("#")[1];
          let action = subscribeButton.innerText;
          const res = await fetch(
            `../../api/lists/${list_id}/list_change_subscribtion_status/`,
            get_fetch_settings("POST")
          );
          if (!res.ok) {
            showMessage("Error: Network request failed unexpectedly!", "Error");
          } else {
            const context = await res.json();
            console.log(action);
            if (action == "Subscribe") {
              subscribeButton.classList.add("listSubscribed");
              subscribeButton.innerText = "Subscribed";
              showMessage(context, "Success");
            } else {
              subscribeButton.classList.remove("listSubscribed");
              subscribeButton.innerText = "Subscribe";
              showMessage(context, "Remove");
            }
          }
        } catch (e) {
          // showMessage("Error: Unexpected error has occurred!", "Error");
        }
      }
    });
  }
});

// list delete

document.querySelectorAll(".listDeleteButton").forEach((listDeleteButton) => {
  listDeleteButton.addEventListener("click", async () => {
    try {
      const list_id = listDeleteButton
        .closest(".contentWrapper")
        .id.split("#")[1];
      const res = await fetch(
        `../../api/lists/${list_id}/`,
        get_fetch_settings("DELETE")
      );
      if (!res.ok) {
        showMessage("Error: Network request failed unexpectedly!", "Error");
      } else {
        const context = await res.json();
        listDeleteButton.closest(".contentWrapper").remove();
        showMessage(context, "Remove");
      }
    } catch (e) {
      // showMessage("Error: Unexpected error has occurred!", "Error");
    }
  });
});

//change tabs
const feedTabs = document.querySelectorAll(".feedTabsContainer button");
const tabsContent = document.querySelectorAll(".tabsContent");

feedTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    for (let i = 0, j = feedTabs.length; i < j; i++) {
      feedTabs[i].classList.remove("activatedTab");
      tabsContent[i].classList.remove("tabsContentActive");
    }
    feedTabs[tab.dataset.forTab].classList.add("activatedTab");
    tabsContent[tab.dataset.forTab].classList.add("tabsContentActive");
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
                sourceName.id = `fass?si#${source.source_id}`;
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
                          removeSourceButton
                            .closest(".searchResult")
                            .querySelector("span")
                            .id.split("#")[1]
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
                listName.id = `flls?li#${list.list_id}`;
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
                          removeListButton
                            .closest(".searchResult")
                            .querySelector("span")
                            .id.split("#")[1]
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

document
  .querySelector(".feedTabsContainer .fa-plus")
  .addEventListener("click", () => {
    const activatedTab = document.querySelector(".activatedTab").innerText;
    if (activatedTab === "Your Lists") {
      document.querySelector(
        ".popupContainer .createListPopup .formContainer"
      ).style.display = "flex";
    } else if (activatedTab === "Subscribed Lists") {
      document.querySelector(
        ".popupContainer .addListsPopup .formContainer"
      ).style.display = "flex";
    } else if (activatedTab === "Subscribed Sources") {
      document.querySelector(
        ".popupContainer .addSourcesPopup .formContainer"
      ).style.display = "flex";
    }
    document.querySelector(".classicMain").style.opacity = "0.1";
    document.querySelector(".popupContainer").style.display = "block";
  });

document
  .querySelectorAll(".popupContainer .formHeaderContainer .fa-times")
  .forEach((closeButton) => {
    closeButton.addEventListener("click", () => {
      document.querySelector(".classicMain").style.opacity = "1";
      document.querySelector(".popupContainer").style.display = "none";
      closeButton
        .closest(".popup")
        .querySelector(".formContainer").style.display = "none";
    });
  });

document
  .querySelectorAll(".slider .contentWrapper .infoButton")
  .forEach((infoButton) => {
    infoButton.addEventListener("click", () => {
      document.querySelector(".popupContainer .listInfoPopup").style.display =
        "flex";
    });
  });
