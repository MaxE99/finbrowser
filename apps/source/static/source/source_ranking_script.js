document
  .querySelectorAll(".sourceRankingContainer .subscribeButton")
  .forEach((subscribeButton) => {
    subscribeButton.addEventListener("click", async () => {
      try {
        const source_id = subscribeButton
          .closest(".sourceRankingContainer")
          .id.split("#")[1];
        const action = subscribeButton.innerText;
        const res = await fetch(
          `../../api/sources/${source_id}/source_change_subscribtion_status/`,
          get_fetch_settings("POST")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          const context = await res.json();
          if (action == "Subscribe") {
            subscribeButton.classList.add("subscribed");
            subscribeButton.innerText = "Subscribed";
            showMessage(context, "Success");
          } else {
            subscribeButton.classList.remove("subscribed");
            subscribeButton.innerText = "Subscribe";
            showMessage(context, "Remove");
          }
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
    });
  });

// dropdown
document
  .querySelectorAll(".filterSidebar .dropdown")
  .forEach((dropdownButton) =>
    dropdownButton.addEventListener("click", (e) => {
      e.target.querySelector("ul").style.display !== "block"
        ? (e.target.querySelector("ul").style.display = "block")
        : (e.target.querySelector("ul").style.display = "none");
    })
  );

function selectFilterOption(selection) {
  const selectContainer = selection.closest(".selectContainer");
  const selectedOptionsContainer = selectContainer.nextElementSibling;
  const clonedSelection = selection.cloneNode(true);
  clonedSelection.classList.add("selectedOption");
  const deleteSelectionButton = document.createElement("i");
  deleteSelectionButton.classList.add("fas", "fa-times");
  deleteSelectionButton.addEventListener("click", () => {
    if (
      selectContainer.querySelector(
        `ul li[value=${clonedSelection.getAttribute("value")}`
      )
    ) {
      selectContainer.querySelector(
        `ul li[value=${clonedSelection.getAttribute("value")}`
      ).style.display = "flex";
    }
    clonedSelection.remove();
    if (selectedOptionsContainer.querySelectorAll("li").length === 0) {
      selectedOptionsContainer.style.display = "none";
    }
  });
  clonedSelection.appendChild(deleteSelectionButton);
  selection.style.display = "none";
  selectedOptionsContainer.appendChild(clonedSelection);
  selectedOptionsContainer.style.display = "block";
  selectContainer.querySelector("ul").style.display = "none";
}

// search tags
document
  .getElementById("tagAutocomplete")
  .addEventListener("keyup", async function () {
    let search_term = document.getElementById("tagAutocomplete").value;
    let results_list = document.querySelector("#tagAutocomplete_result ul");
    if (search_term && search_term.replaceAll(/\s/g, "") != "") {
      try {
        const res = await fetch(
          `../../../../../../api/source_tags/?search_term=${search_term}`,
          get_fetch_settings("GET")
        );
        if (!res.ok) {
          showMessage("Error: Network request failed unexpectedly!", "Error");
        } else {
          const context = await res.json();
          let selectedTags = [];
          document
            .querySelectorAll(".selectedTagsContainer li")
            .forEach((result) => selectedTags.push(result.innerText));
          results_list.style.display = "block";
          results_list.innerHTML = "";
          if (context.length > 0) {
            context.forEach((tag) => {
              if (!selectedTags.includes(tag.name)) {
                const tagOption = document.createElement("li");
                tagOption.setAttribute("value", tag.name);
                tagOption.innerText = tag.name;
                tagOption.addEventListener("click", () => {
                  selectFilterOption(tagOption);
                });
                results_list.appendChild(tagOption);
              }
            });
          }
        }
      } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
      }
      document.onclick = function (e) {
        if (e.target.id !== "autocomplete_list_results") {
          results_list.style.display = "none";
          document.querySelector(".mainInputSearch").style.borderRadius =
            "0.8rem";
        }
      };
    } else {
      results_list.style.display = "none";
      document.querySelector(".mainInputSearch").style.borderRadius = "0.8rem";
    }
  });

// filter selection
document
  .querySelectorAll(".filterSidebar .selectionList li")
  .forEach((selection) => {
    selection.addEventListener("click", () => {
      selectFilterOption(selection);
    });
  });

//open add list to sources form
document
  .querySelectorAll(".sourceAddToListButton")
  .forEach((addSourceButton) => {
    addSourceButton.addEventListener("click", () => {
      document
        .querySelectorAll(".addSourceToListForm")
        .forEach((form) => (form.style.display = "none"));
      document
        .querySelectorAll(".sourcesCreateListMenu")
        .forEach((menu) => (menu.style.display = "none"));
      addSourceButton
        .closest(".fourthRow")
        .querySelector(".addSourceToListForm").style.display = "block";
    });
  });

//close add list sources form

document
  .querySelectorAll(".addSourceToListForm .fa-times")
  .forEach((closeAddSourceFormButton) => {
    closeAddSourceFormButton.addEventListener("click", () => {
      document.querySelector(".addSourceToListForm").style.display = "none";
    });
  });

// add sources to lists

function check_list_status(saveButton) {
  let add_list_ids = [];
  let remove_list_ids = [];
  const input_list = saveButton
    .closest(".addSourceToListForm")
    .querySelectorAll(".listContainer input");
  for (let i = 0, j = input_list.length; i < j; i++) {
    if (
      input_list[i].className === "sourceInList" &&
      input_list[i].checked === false
    ) {
      remove_list_ids.push(input_list[i].id.split("id_list_")[1]);
    } else if (
      input_list[i].className === "sourceNotInList" &&
      input_list[i].checked
    ) {
      add_list_ids.push(input_list[i].id.split("id_list_")[1]);
    }
  }
  return [add_list_ids, remove_list_ids];
}

document
  .querySelectorAll(".addSourceToListForm .saveButton")
  .forEach((saveButton) => {
    saveButton.addEventListener("click", async () => {
      let source_id = saveButton
        .closest(".sourceRankingContainer")
        .id.split("#")[1];
      const [add_lists, remove_lists] = check_list_status(saveButton);
      body = {
        source_id: source_id,
        add_lists: add_lists,
        remove_lists: remove_lists,
      };
      try {
        const res = await fetch(
          `../../api/lists/change_source_status_from_lists/`,
          {
            method: "POST",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            mode: "same-origin",
            body: JSON.stringify(body),
          }
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
    });
  });
