// add Sources Search
let selected_sources = [];
document
  .getElementById("addSourcesInput")
  .addEventListener("keyup", async function (e) {
    let search_term = document.getElementById("addSourcesInput").value;
    let results_list = document.getElementById("sourceSearchResults");
    let selected_list = document.querySelector(".selectedSourcesContainer");
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const list_id = url.substring(index + 1);
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      results_list.style.display = "block";
      selected_list.style.display = "none";
      try {
        const res = await fetch(
          `../../api/search_sources/${list_id}/${search_term}`,
          get_fetch_settings("GET")
        );
        if (!res.ok) {
          showMessage("Error: Site couldn't be searched!", "Error");
        } else {
          const context = await res.json();
          results_list.innerHTML = "";
          if (context.length > 0) {
            const resultHeader = document.createElement("div");
            resultHeader.innerText = "Results:";
            results_list.append(resultHeader);
            context.forEach((source) => {
              if (selected_sources.includes(source.domain) == false) {
                const searchResult = document.createElement("div");
                searchResult.classList.add("searchResult");
                const resultImage = document.createElement("img");
                resultImage.src = `/static/${source.favicon_path}`;
                const sourceName = document.createElement("span");
                sourceName.innerText = source.domain;
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
                    selected_sources.push(source.domain);
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
                    document.getElementById("addSourcesInput").value = "";
                  }
                );
              }
            });
          }
        }
      } catch (e) {
        showMessage("Error: Network error detected!", "Error");
      }
    } else {
      results_list.style.display = "none";
      selected_list.style.display = "block";
    }
  });

//open add sources menu
if (document.querySelector(".addSourcesButton")) {
  document.querySelector(".addSourcesButton").addEventListener("click", () => {
    document.querySelector(".addSourcesForm").style.display = "flex";
    document.querySelector(".listOverlay").style.opacity = "0.5";
  });
}

//close add sources menu
document
  .querySelector(".addSourcesCloseButton")
  .addEventListener("click", () => {
    document.querySelector(".addSourcesForm").style.display = "none";
    document.querySelector(".listOverlay").style.opacity = "1";
  });

// add/confirm sources to list
document
  .querySelector(".addSourcesForm button")
  .addEventListener("click", async () => {
    const url = window.location.href;
    const index = url.lastIndexOf("/");
    const list_id = url.substring(index + 1);
    if (selected_sources.length) {
      try {
        const res = await fetch(
          `../api/add_sources/${selected_sources}/${list_id}`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: List can't be subscribed!", "Error");
        } else {
          const context = await res.json();
          showMessage(context, "Success");
          window.location.reload();
        }
      } catch (e) {
        showMessage("Error: Network error detected!", "Error");
      }
    } else {
      showMessage("You need to select sources!", "Error");
    }
  });
