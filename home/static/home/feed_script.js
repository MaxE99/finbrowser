// Open settings menu
document
  .querySelector(".interactionWrapper .createListButton")
  .addEventListener("click", () => {
    document.querySelector(
      ".interactionWrapper .createListMenu"
    ).style.display = "flex";
  });

// Close menus
document
  .querySelector(".interactionWrapper .closeFormContainerButton")
  .addEventListener("click", () => {
    document.querySelector(
      ".interactionWrapper .createListMenu"
    ).style.display = "none";
  });

//open add sources menu
if (document.querySelector(".addSourcesButton")) {
  document.querySelector(".addSourcesButton").addEventListener("click", () => {
    document.querySelector(".addSourcesForm").style.display = "flex";
  });
}

//close add sources menu
document
  .querySelector(".addSourcesForm .closeFormContainerButton")
  .addEventListener("click", () => {
    document.querySelector(".addSourcesForm").style.display = "none";
  });

// add Sources Search
let selected_sources = [];
document
  .querySelector(".addSourcesForm #textInput")
  .addEventListener("keyup", async function (e) {
    let search_term = document.querySelector(
      ".addSourcesForm #textInput"
    ).value;
    let results_list = document.querySelector(
      ".addSourcesForm #searchResultsContainer"
    );
    let selected_list = document.querySelector(
      ".addSourcesForm .selectionContainer"
    );
    // die art an list_id heranzukommen unterscheidet sich überall von daher muss ich das anpassen, wenn ich refactore und alles zusammenlege
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      results_list.style.display = "block";
      selected_list.style.display = "none";
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/sources/?feed_search=${search_term}`,
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
              if (selected_sources.includes(source.name) == false) {
                const searchResult = document.createElement("div");
                searchResult.classList.add("searchResult");
                const resultImage = document.createElement("img");
                resultImage.src = `/static/${source.favicon_path}`;
                const sourceName = document.createElement("span");
                sourceName.innerText = source.name;
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
                    selected_sources.push(source.name);
                    const removeSourceButton = document.createElement("i");
                    removeSourceButton.classList.add("fas", "fa-trash");
                    removeSourceButton.addEventListener("click", () => {
                      removeSourceButton.parentElement.remove();
                      selected_sources = selected_sources.filter(function (e) {
                        return (
                          e !==
                          removeSourceButton.previousElementSibling.innerText
                        );
                      });
                    });
                    searchResult.appendChild(removeSourceButton);
                    selected_list.appendChild(searchResult);
                    results_list.style.display = "none";
                    selected_list.style.display = "block";
                    document.querySelector(".addSourcesForm #textInput").value =
                      "";
                  }
                );
              }
            });
          }
        }
      } catch (e) {
        showMessage("Error: Unexpected error has occurred!", "Error");
      }
    } else {
      results_list.style.display = "none";
      selected_list.style.display = "block";
    }
  });

// add/confirm sources to list
document
  .querySelector(".addSourcesForm .formSubmitButton")
  .addEventListener("click", async () => {
    if (selected_sources.length) {
      for (let i = 0, j = selected_sources.length; i < j; i++) {
        try {
          const res = await fetch(
            `../api/source_change_subscribtion_status/${selected_sources[i]}`,
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
          showMessage("Error: Unexpected error has occurred!", "Error");
        }
      }
    } else {
      showMessage("You need to select sources!", "Error");
    }
  });

// add list Search
// add list Search
// add list Search
// add list Search
// add list Search

//open add lists menu
if (document.querySelector(".addListsButton")) {
  document.querySelector(".addListsButton").addEventListener("click", () => {
    document.querySelector(".addListsForm").style.display = "flex";
  });
}

//close add lists menu
document
  .querySelector(".addListsForm .closeFormContainerButton")
  .addEventListener("click", () => {
    document.querySelector(".addListsForm").style.display = "none";
  });

let selected_lists = [];
document
  .querySelector(".addListsForm #textInput")
  .addEventListener("keyup", async function (e) {
    let search_term = document.querySelector(".addListsForm #textInput").value;
    let results_list = document.querySelector(
      ".addListsForm #searchResultsContainer"
    );
    let selected_list = document.querySelector(
      ".addListsForm .selectionContainer"
    );
    // die art an list_id heranzukommen unterscheidet sich überall von daher muss ich das anpassen, wenn ich refactore und alles zusammenlege
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      results_list.style.display = "block";
      selected_list.style.display = "none";
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/lists/?feed_search=${search_term}`,
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
                  resultImage.src = "/static/home/media/bigger_favicon.png";
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
                          removeListButton.previousElementSibling.id.replace(
                            "list_",
                            ""
                          )
                        );
                      });
                      removeListButton.parentElement.remove();
                    });
                    searchResult.appendChild(removeListButton);
                    selected_list.appendChild(searchResult);
                    results_list.style.display = "none";
                    selected_list.style.display = "block";
                    document.querySelector(".addListsForm #textInput").value =
                      "";
                  }
                );
              }
            });
          }
        }
      } catch (e) {
        showMessage("Error: Unexpected error has occurred!", "Error");
      }
    } else {
      results_list.style.display = "none";
      selected_list.style.display = "block";
    }
  });

// add/confirm lists
document
  .querySelector(".addListsForm button")
  .addEventListener("click", async () => {
    if (selected_lists.length) {
      for (let i = 0, j = selected_lists.length; i < j; i++) {
        try {
          const res = await fetch(
            `../api/list_change_subscribtion_status/${selected_lists[i]}`,
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
          showMessage("Error: Unexpected error has occurred!", "Error");
        }
      }
    } else {
      showMessage("You need to select sources!", "Error");
    }
  });

// open add external link menu
document
  .querySelector(".addExternalLinkButton")
  .addEventListener("click", () => {
    document.querySelector(".addExternalLinksContainer").style.display = "flex";
  });

// close external link menu
document
  .querySelector(".addExternalLinksContainer .closeFormContainerButton")
  .addEventListener("click", () => {
    document.querySelector(".addExternalLinksContainer").style.display = "none";
  });

// Caroussell

// document.addEventListener("click", (e) => {
//   let handle;
//   if (e.target.matches(".handle")) {
//     handle = e.target;
//   } else {
//     handle = e.target.closest(".handle");
//   }
//   if (handle != null) onHandleClick(handle);
// });

// const throttleProgressBar = throttle(() => {
//   document.querySelectorAll(".progress-bar").forEach(calculateProgressBar);
// }, 250);
// window.addEventListener("resize", throttleProgressBar);

// document.querySelectorAll(".progress-bar").forEach(calculateProgressBar);

// function calculateProgressBar(progressBar) {
//   progressBar.innerHTML = "";
//   const slider = progressBar.closest(".row").querySelector(".slider");
//   const itemCount = slider.children.length;
//   const itemsPerScreen = parseInt(
//     getComputedStyle(slider).getPropertyValue("--items-per-screen")
//   );
//   let sliderIndex = parseInt(
//     getComputedStyle(slider).getPropertyValue("--slider-index")
//   );
//   const progressBarItemCount = Math.ceil(itemCount / itemsPerScreen);

//   if (sliderIndex >= progressBarItemCount) {
//     slider.style.setProperty("--slider-index", progressBarItemCount - 1);
//     sliderIndex = progressBarItemCount - 1;
//   }

//   for (let i = 0; i < progressBarItemCount; i++) {
//     const barItem = document.createElement("div");
//     barItem.classList.add("progress-item");
//     if (i === sliderIndex) {
//       barItem.classList.add("active");
//     }
//     progressBar.append(barItem);
//   }
// }

// function onHandleClick(handle) {
//   const progressBar = handle.closest(".row").querySelector(".progress-bar");
//   const slider = handle.closest(".container").querySelector(".slider");
//   const sliderIndex = parseInt(
//     getComputedStyle(slider).getPropertyValue("--slider-index")
//   );
//   const progressBarItemCount = progressBar.children.length;
//   if (handle.classList.contains("left-handle")) {
//     if (sliderIndex - 1 < 0) {
//       slider.style.setProperty("--slider-index", progressBarItemCount - 1);
//       progressBar.children[sliderIndex].classList.remove("active");
//       progressBar.children[progressBarItemCount - 1].classList.add("active");
//     } else {
//       slider.style.setProperty("--slider-index", sliderIndex - 1);
//       progressBar.children[sliderIndex].classList.remove("active");
//       progressBar.children[sliderIndex - 1].classList.add("active");
//     }
//   }

//   if (handle.classList.contains("right-handle")) {
//     if (sliderIndex + 1 >= progressBarItemCount) {
//       slider.style.setProperty("--slider-index", 0);
//       progressBar.children[sliderIndex].classList.remove("active");
//       progressBar.children[0].classList.add("active");
//     } else {
//       slider.style.setProperty("--slider-index", sliderIndex + 1);
//       progressBar.children[sliderIndex].classList.remove("active");
//       progressBar.children[sliderIndex + 1].classList.add("active");
//     }
//   }
// }

// function throttle(cb, delay = 1000) {
//   let shouldWait = false;
//   let waitingArgs;
//   const timeoutFunc = () => {
//     if (waitingArgs == null) {
//       shouldWait = false;
//     } else {
//       cb(...waitingArgs);
//       waitingArgs = null;
//       setTimeout(timeoutFunc, delay);
//     }
//   };

//   return (...args) => {
//     if (shouldWait) {
//       waitingArgs = args;
//       return;
//     }

//     cb(...args);
//     shouldWait = true;
//     setTimeout(timeoutFunc, delay);
//   };
// }
