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

// select tags for filtering from source container
document.querySelectorAll(".thirdRow .tag").forEach((tag) =>
  tag.addEventListener("click", () => {
    const selectedTagsContainer = document.querySelector(
      ".selectedTagsContainer"
    );
    const selectedTags = [];
    selectedTagsContainer.querySelectorAll("li").forEach((sTag) => {
      selectedTags.push(sTag.innerText);
    });
    if (!selectedTags.includes(tag.innerText)) {
      const li = document.createElement("li");
      li.classList.add("selectedOption");
      li.setAttribute("value", tag.innerText);
      li.innerText = tag.innerText;
      const input = document.createElement("input");
      input.setAttribute("hidden", true);
      input.setAttribute("name", "tag");
      input.setAttribute("value", tag.innerText);
      const deleteButton = document.createElement("i");
      li.appendChild(input);
      li.appendChild(deleteButton);
      deleteButton.classList.add("fas", "fa-times");
      deleteButton.addEventListener("click", () => {
        li.remove();
      });
      selectedTagsContainer.appendChild(li);
    }
  })
);

// remove selected tags on click
document
  .querySelectorAll(".selectedTagsContainer li i")
  .forEach((deleteButton) =>
    deleteButton.addEventListener("click", () => {
      deleteButton.closest("li").remove();
    })
  );

// dropdown
document.querySelectorAll("form .dropdown").forEach((dropdownButton) => {
  dropdownButton.addEventListener("click", (e) => {
    e.target.querySelector("ul").style.display !== "block"
      ? (e.target.querySelector("ul").style.display = "block")
      : (e.target.querySelector("ul").style.display = "none");
  });
  document.onclick = function (e) {
    if (!e.target.closest("ul") && e.target !== dropdownButton) {
      dropdownButton.querySelector("ul").style.display = "none";
    }
  };
});

function selectFilterOption(selection) {
  const selectContainer = selection.closest(".selectContainer");
  const selectedTagsContainer = selection
    .closest("form")
    .querySelector(".selectedTagsContainer");
  const clonedSelection = selection.cloneNode(true);
  clonedSelection.classList.add("selectedOption");
  const deleteSelectionButton = document.createElement("i");
  deleteSelectionButton.classList.add("fas", "fa-times");
  deleteSelectionButton.addEventListener("click", () => {
    clonedSelection.remove();
  });
  const hiddenInput = document.createElement("input");
  hiddenInput.setAttribute("hidden", true);
  hiddenInput.setAttribute("name", "tag");
  hiddenInput.setAttribute("value", clonedSelection.innerText);
  clonedSelection.appendChild(hiddenInput);
  clonedSelection.appendChild(deleteSelectionButton);
  selection.style.display = "none";
  selectedTagsContainer.appendChild(clonedSelection);
  selectedTagsContainer.style.display = "flex";
  selectContainer.querySelector("ul").style.display = "none";
}

// search tags
document.querySelectorAll("form .mainInputSearch").forEach((searchInput) =>
  searchInput.addEventListener("keyup", async function () {
    let search_term = searchInput.value;
    let results_list = searchInput
      .closest("form")
      .querySelector("#tagAutocomplete_result ul");
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
        }
      };
    } else {
      results_list.style.display = "none";
    }
  })
);

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

// openFiltersMenu
document.querySelector(".openFiltersButton").addEventListener("click", () => {
  document.querySelector(".horizontalFilterMenu").style.display = "flex";
  document.querySelector(".pageWrapper").style.opacity = "0.1";
});

// closeFiltersMenu
document
  .querySelector(".horizontalFilterMenu .discardButton")
  .addEventListener("click", () => {
    document.querySelector(".horizontalFilterMenu").style.display = "none";
    document.querySelector(".pageWrapper").removeAttribute("style");
  });
